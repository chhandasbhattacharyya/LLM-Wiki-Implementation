# Readwise Reader Export Guide

How to collect sources using Readwise Reader and feed them into the LLM Wiki.

---

## Step 1 — Save articles in Readwise Reader

Use Readwise Reader to save articles, newsletters, PDFs, and web pages:

- **Browser extension**: Install the Readwise Reader browser extension and click it on any page to save it
- **Email newsletter**: Forward newsletters to your personal Readwise inbox address (found in Reader settings)
- **RSS feeds**: Subscribe to feeds directly inside Reader
- **Mobile**: Use the share sheet on iOS/Android to send pages to Reader

Readwise Reader saves the full article content, not just a link.

---

## Step 2 — Highlight and annotate while reading

This is where your curation happens. As you read inside Reader:

- **Highlight** key passages by selecting text — these become the high-weight content the LLM synthesises from
- **Add a note** to any highlight (tap/click the note icon after highlighting) — these become "Open Questions" or "Notes" in your wiki page, not source facts
- **Tag** documents inside Reader if you want — tags are included in some export formats

The more intentional your highlights, the richer the resulting wiki pages.

---

## Step 3 — Export from Readwise

### Option A: API sync script (recommended)

`scripts/readwise_sync.py` handles everything automatically — fetching highlights, grouping them by source document, writing markdown files, and tracking what has already been exported so only new highlights are fetched on subsequent runs.

**One-time setup:**

```bash
pip install requests python-dotenv
```

Get your API token from [readwise.io/access_token](https://readwise.io/access_token) and add it to a `.env` file at the repo root:

```
READWISE_TOKEN=your_token_here
```

**Run the sync:**

```bash
python scripts/readwise_sync.py
```

First run exports everything. Subsequent runs only fetch highlights updated since the last run. Files land directly in `sources/readwise-exports/` — no zip, no manual steps.

### Option B: Manual export (one-off or batched)

1. Go to [readwise.io/export](https://readwise.io/export)
2. Select **Markdown** as the export format
3. Optionally filter by date range or book/article type
4. Click **Export** — Readwise downloads a zip file
5. Unzip and move the `.md` files into `sources/readwise-exports/` in this repository

---

## Step 4 — Run Ingest

Tell your LLM agent:

```
Read CLAUDE.md and run the Ingest workflow on any unprocessed files in sources/.
```

The LLM will:
- Find files in `sources/readwise-exports/` not yet referenced in any wiki page frontmatter
- Parse the Readwise export format (see below)
- Create or update wiki pages in `wiki/`
- Update `wiki/index.md` and append to `wiki/log.md`

---

## Readwise Export Format Reference

A typical Readwise markdown export looks like this:

```markdown
# Article Title

## Metadata
- Author: Jane Smith
- Full Title: The Full Article Title
- Category: articles
- URL: https://example.com/article
- Document Tags: tag1, tag2
- Date: [[2026-03-15]]

## Highlights

> The key insight is that retrieval systems fail when the query and the document
> use different vocabulary to describe the same concept.

Note: This is exactly the gap RAG tries to bridge — worth cross-referencing

---

> Fine-tuning bakes knowledge into model weights; RAG keeps knowledge external
> and updatable without retraining.

Note: Ask: at what scale does fine-tuning start to outperform RAG?

---
```

### How the LLM processes this format

| Element | How it appears | LLM handling |
|---------|---------------|--------------|
| `## Metadata` block | Top of file | Parsed for `author`, `source_url`, `source_date` frontmatter |
| `> ` blockquote lines | Highlights you selected | Treated as high-weight content — primary synthesis material |
| `Note:` lines | Your annotations on highlights | Filed under "Open Questions" or "Notes" — not treated as source facts |
| `---` separators | Between highlights | Structural only — ignored |
| Document Tags | In Metadata block | Informational — LLM may use to suggest `domain:` tags |

---

## Keeping Track of What Has Been Processed

The LLM tracks processed sources via the `source_file:` frontmatter field in wiki pages — it will skip files already referenced there.

**Do not rename Readwise export files** after dropping them into `sources/readwise-exports/`. The filename is the stable identifier.

If you re-export the same article after adding more highlights, the LLM will detect the filename match and update the existing wiki page rather than creating a duplicate.
