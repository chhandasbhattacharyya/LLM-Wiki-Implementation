#!/usr/bin/env python3
"""
Obsidian vault → sources/obsidian-exports/ sync script.

Copies new or updated markdown files from a designated folder in your Obsidian
vault into sources/obsidian-exports/. Only files newer than the last sync are
copied on subsequent runs.

Usage:
    python scripts/obsidian_sync.py

Configuration (in .env at the repo root):
    OBSIDIAN_VAULT_PATH=C:\\Users\\You\\Documents\\MyVault
    OBSIDIAN_CLIPS_FOLDER=Clippings

Requirements:
    pip install python-dotenv
"""

import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; fall back to env vars

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = REPO_ROOT / "sources" / "obsidian-exports"
CURSOR_FILE = EXPORT_DIR / ".last_sync"  # stores timestamp of last run

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_config() -> tuple[Path, str]:
    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    clips_folder = os.environ.get("OBSIDIAN_CLIPS_FOLDER", "Clippings").strip()

    if not vault_path:
        sys.exit(
            "Error: OBSIDIAN_VAULT_PATH not set.\n"
            "Add it to a .env file at the repo root, e.g.:\n"
            "  OBSIDIAN_VAULT_PATH=C:\\Users\\You\\Documents\\MyVault\n"
            "  OBSIDIAN_CLIPS_FOLDER=Clippings"
        )

    vault = Path(vault_path)
    if not vault.exists():
        sys.exit(f"Error: Vault path does not exist: {vault}")

    return vault, clips_folder


def load_cursor() -> float | None:
    """Return mtime threshold (seconds since epoch), or None for a full sync."""
    if CURSOR_FILE.exists():
        try:
            return float(CURSOR_FILE.read_text().strip())
        except ValueError:
            pass
    return None


def save_cursor(ts: float):
    CURSOR_FILE.write_text(str(ts))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    vault, clips_folder = get_config()
    clips_dir = vault / clips_folder

    if not clips_dir.exists():
        sys.exit(
            f"Error: Clips folder not found: {clips_dir}\n"
            f"Create a folder called '{clips_folder}' in your Obsidian vault,\n"
            f"or set OBSIDIAN_CLIPS_FOLDER to the correct folder name in .env"
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    cursor = load_cursor()
    run_start = datetime.now(timezone.utc).timestamp()

    if cursor:
        since = datetime.fromtimestamp(cursor).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Incremental sync — copying files modified after {since}")
    else:
        print(f"Full sync — copying all markdown files from {clips_dir}")

    md_files = list(clips_dir.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {clips_dir}")
        save_cursor(run_start)
        return

    copied = 0
    skipped = 0
    for src in md_files:
        if cursor and src.stat().st_mtime <= cursor:
            skipped += 1
            continue
        dest = EXPORT_DIR / src.name
        shutil.copy2(src, dest)
        print(f"  Copied: {src.name}")
        copied += 1

    save_cursor(run_start)

    if copied == 0:
        print("No new or updated files since last sync.")
    else:
        print(f"\nDone. {copied} file(s) copied to {EXPORT_DIR.relative_to(REPO_ROOT)}/")
        print("Next step: tell Claude to run the Ingest workflow.")

    if skipped:
        print(f"({skipped} unchanged file(s) skipped)")


if __name__ == "__main__":
    main()
