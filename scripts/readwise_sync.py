#!/usr/bin/env python3
"""
Readwise → sources/readwise-exports/ sync script.

Fetches highlights from the Readwise API and writes one markdown file per
source document into sources/readwise-exports/. On subsequent runs, only
documents with new or updated highlights are re-exported.

Usage:
    READWISE_TOKEN=your_token python scripts/readwise_sync.py

Or with a .env file at the repo root containing:
    READWISE_TOKEN=your_token

Requirements:
    pip install requests python-dotenv
"""

import os
import re
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; fall back to env vars only

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = REPO_ROOT / "sources" / "readwise-exports"
CURSOR_FILE = EXPORT_DIR / ".last_export"   # stores ISO timestamp of last run

API_BASE = "https://readwise.io/api/v2"
PAGE_SIZE = 100  # max allowed by Readwise

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_token() -> str:
    token = os.environ.get("READWISE_TOKEN", "").strip()
    if not token:
        sys.exit(
            "Error: READWISE_TOKEN not set.\n"
            "Export it as an environment variable or add it to a .env file at the repo root."
        )
    return token


def api_get(session: requests.Session, path: str, params: dict = None) -> dict:
    """GET from Readwise API with simple rate-limit retry."""
    url = f"{API_BASE}/{path.lstrip('/')}/"
    while True:
        resp = session.get(url, params=params or {})
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 5))
            print(f"  Rate limited — waiting {wait}s …")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()


def paginate(session: requests.Session, path: str, params: dict = None):
    """Yield all results across paginated Readwise API responses."""
    params = dict(params or {})
    params["page_size"] = PAGE_SIZE
    page = 1
    while True:
        params["page"] = page
        data = api_get(session, path, params)
        yield from data.get("results", [])
        if not data.get("next"):
            break
        page += 1


def slugify(text: str) -> str:
    """Convert a title to a safe filename (no UUID — title is stable enough)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-")
    return text[:80] or "untitled"


def load_cursor() -> str | None:
    """Return ISO timestamp of last run, or None for a full export."""
    if CURSOR_FILE.exists():
        ts = CURSOR_FILE.read_text().strip()
        return ts if ts else None
    return None


def save_cursor(ts: str):
    CURSOR_FILE.write_text(ts)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_document(book: dict, highlights: list[dict]) -> str:
    """Render one source document as the markdown format CLAUDE.md expects."""
    title = book.get("title") or "Untitled"
    author = book.get("author") or ""
    url = book.get("source_url") or book.get("unique_url") or ""
    category = book.get("category") or ""
    tags = book.get("document_note") or ""  # Readwise doesn't expose doc tags via v2; placeholder

    # Use asin_or_isbn as date fallback; prefer highlighted_at of first highlight
    date_str = ""
    if highlights:
        raw = highlights[0].get("highlighted_at") or ""
        if raw:
            try:
                date_str = datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            except ValueError:
                date_str = raw[:10]

    lines = [f"# {title}", "", "## Metadata"]
    if author:
        lines.append(f"- Author: {author}")
    lines.append(f"- Full Title: {title}")
    if category:
        lines.append(f"- Category: {category}")
    if url:
        lines.append(f"- URL: {url}")
    if date_str:
        lines.append(f"- Date: {date_str}")

    lines += ["", "## Highlights", ""]

    for h in highlights:
        text = (h.get("text") or "").strip()
        note = (h.get("note") or "").strip()
        if not text:
            continue
        # Wrap each highlight line in blockquote
        quoted = "\n".join(f"> {line}" if line else ">" for line in text.splitlines())
        lines.append(quoted)
        if note:
            lines.append("")
            lines.append(f"Note: {note}")
        lines += ["", "---", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    token = get_token()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"Authorization": f"Token {token}"})

    cursor = load_cursor()
    run_start = datetime.now(timezone.utc).isoformat()

    if cursor:
        print(f"Incremental export — fetching highlights updated after {cursor}")
    else:
        print("Full export — fetching all highlights (this may take a while) …")

    # Fetch highlights (optionally filtered by updated_after)
    params = {}
    if cursor:
        params["updated_after"] = cursor

    print("Fetching highlights …")
    highlights_by_book: dict[int, list[dict]] = {}
    for h in paginate(session, "highlights", params):
        book_id = h.get("book_id")
        if book_id is not None:
            highlights_by_book.setdefault(book_id, []).append(h)

    if not highlights_by_book:
        print("No new highlights since last export.")
        save_cursor(run_start)
        return

    print(f"Found highlights across {len(highlights_by_book)} document(s). Fetching document metadata …")

    # Fetch book metadata for affected books only
    books: dict[int, dict] = {}
    for book in paginate(session, "books"):
        if book["id"] in highlights_by_book:
            books[book["id"]] = book

    # Write one file per document
    written = 0
    for book_id, highlights in highlights_by_book.items():
        book = books.get(book_id)
        if not book:
            print(f"  Warning: no metadata found for book_id={book_id}, skipping")
            continue

        title = book.get("title") or "Untitled"
        filename = f"{slugify(title)}.md"
        filepath = EXPORT_DIR / filename

        # Sort highlights by location/order
        highlights.sort(key=lambda h: (h.get("location") or 0, h.get("id") or 0))

        content = render_document(book, highlights)
        filepath.write_text(content, encoding="utf-8")
        print(f"  Wrote {filename}  ({len(highlights)} highlight(s))")
        written += 1

    save_cursor(run_start)
    print(f"\nDone. {written} file(s) written to {EXPORT_DIR.relative_to(REPO_ROOT)}/")
    print("Next step: tell Claude to run the Ingest workflow.")


if __name__ == "__main__":
    main()
