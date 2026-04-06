# Notion Export Guide

How to collect sources using Notion and feed them into the LLM Wiki.

---

## Step 1 — Clip web articles into Notion

Install the **Notion Web Clipper** browser extension (Chrome or Firefox):
- Chrome: search "Notion Web Clipper" in the Chrome Web Store
- Firefox: search "Notion Web Clipper" on Firefox Add-ons

When you find an article or page you want to add to your knowledge base:
1. Click the Notion Web Clipper icon in your browser toolbar.
2. Select the Notion workspace and database/page where clipped content should land.
3. Click **Save page**. Notion saves a copy of the full article as a Notion page.

**Tip:** Create a dedicated Notion database called "Sources" or "Inbox" to keep clipped articles organised before processing them.

---

## Step 2 — Annotate in Notion (optional but recommended)

Before exporting, you can enrich the clipped page inside Notion:

- Highlight important passages using Notion's **callout blocks** (`/callout`) — the LLM will treat these as user-highlighted content and weight them more heavily during synthesis.
- Add personal notes or questions directly in the page body. The LLM will file these under "Open Questions" in the wiki rather than treating them as source facts.
- Add Notion properties (tags, dates, etc.) to the page — these will appear in the export's property table and will be stripped by the LLM (they are workspace metadata, not knowledge).

---

## Step 3 — Export from Notion

### Exporting a single page:
1. Open the page in Notion.
2. Click the **"..."** (More) menu in the top-right corner.
3. Select **Export**.
4. Set format to **Markdown & CSV**.
5. Toggle **Include subpages** as needed.
6. Click **Export**. Notion downloads a `.zip` file.

### Exporting multiple pages at once:
1. Open the database or parent page containing the pages you want to export.
2. Click **"..."** → **Export**.
3. Set format to **Markdown & CSV**, enable **Include subpages**.
4. Click **Export**. All pages export as a single `.zip`.

---

## Step 4 — Add to the repository

1. Unzip the downloaded `.zip` file.
2. Move the resulting `.md` files into `sources/notion-exports/` in this repository.
   - If Notion included image folders (e.g. `My Article <uuid>/`), you can include them too, but the LLM will ignore broken image paths.
   - **Do not rename the files.** The Notion-generated filename (page title + UUID) becomes the canonical source reference in wiki frontmatter.
3. Stage the new files:
   ```bash
   git add sources/notion-exports/
   ```
4. You do not need to commit before running the LLM — but committing keeps a clean history of what sources were added when.

---

## Step 5 — Run Ingest

Open Claude Code (or your LLM agent of choice) and run the Ingest workflow:

```
Read CLAUDE.md and run the Ingest workflow on any unprocessed files in sources/.
```

The LLM will:
- Read each new source file
- Strip Notion metadata tables
- Identify what kind of knowledge it contains
- Create or update wiki pages in `wiki/`
- Update `wiki/index.md` and append to `wiki/log.md`

---

## Notes on Notion Export Format

Notion exports have some quirks the LLM is configured to handle:

| Notion feature | How it appears in export | LLM handling |
|----------------|--------------------------|--------------|
| Page properties | Key-value block at top of file | Stripped — workspace metadata |
| Callout blocks | `> ` blockquotes | Treated as user highlights — weighted higher |
| Toggle blocks | Flattened to plain text | Treated as regular content |
| Inline comments | Not included in export | N/A |
| Images | Broken relative paths | Ignored; alt-text used if substantive |
| Linked databases | Rendered as tables | Treated as regular table content |
| Page title | `# Title` heading at top | Used as the reference title |

---

## Keeping Sources Organised

Recommended Notion structure before export:

```
Notion Workspace/
└── Sources (database)
    ├── 📋 Properties: Status (To Process / Processed), Domain, Date Clipped
    ├── Article 1
    ├── Article 2
    └── ...
```

After the LLM processes a source, mark it as **Processed** in Notion so you know not to re-export it. The LLM also tracks processed sources via frontmatter — it will skip files already referenced in wiki pages.
