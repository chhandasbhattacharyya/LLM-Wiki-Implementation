# Obsidian Export Guide

How to collect sources using Obsidian Web Clipper and feed them into the LLM Wiki.

---

## Step 1 — Install Obsidian and create a vault

Download Obsidian from obsidian.md (free). Create a new vault — a vault is just a folder on your computer where Obsidian stores markdown files. A good location is `Documents\MyVault`.

---

## Step 2 — Install Obsidian Web Clipper

Install the **Obsidian Web Clipper** browser extension:
- Chrome / Edge: search "Obsidian Web Clipper" in the Chrome Web Store
- Firefox: search "Obsidian Web Clipper" on Firefox Add-ons

After installing, open the extension settings and point it at your vault.

Set the **save location** to a folder called `Clippings` inside your vault (Obsidian Web Clipper will create it automatically on first use).

---

## Step 3 — Clip articles while browsing

When you find an article worth keeping:
1. Click the **Obsidian Web Clipper** extension icon
2. Optionally edit the title or add tags before saving
3. Click **Save** — the article is saved as a markdown file in your vault's `Clippings` folder

---

## Step 4 — Annotate in Obsidian (optional but recommended)

Open the clipped file in Obsidian and enrich it before syncing:

- **Highlight key passages** using `==double equals==` syntax — the LLM treats these as your curated high-weight content during synthesis
- **Add personal notes** using Obsidian callout blocks — the LLM files these under "Open Questions", not as source facts:
  ```
  > [!note]
  > My thought on this passage
  ```
- **Add tags** in the frontmatter if you want to hint at the domain

---

## Step 5 — Configure the sync script

Add these two lines to your `.env` file at the repo root:

```
OBSIDIAN_VAULT_PATH=C:\Users\YourName\Documents\MyVault
OBSIDIAN_CLIPS_FOLDER=Clippings
```

Replace `C:\Users\YourName\Documents\MyVault` with the actual path to your vault folder. `OBSIDIAN_CLIPS_FOLDER` is the subfolder inside the vault where Web Clipper saves articles — default is `Clippings`.

---

## Step 6 — Run the sync script

```powershell
python scripts/obsidian_sync.py
```

The script copies any new or updated markdown files from your vault's Clippings folder into `sources/obsidian-exports/`. Subsequent runs are incremental — only files modified since the last sync are copied.

---

## Step 7 — Run Ingest

Tell Claude:

```
Read CLAUDE.md and run the Ingest workflow on any unprocessed files in sources/.
```

---

## Obsidian Web Clipper Export Format Reference

A typical clipped file looks like this:

```markdown
---
title: The Illustrated Transformer
source: https://jalammar.github.io/illustrated-transformer/
author: Jay Alammar
date: 2026-04-13
tags: [machine-learning, transformers]
---

# The Illustrated Transformer

The transformer architecture abandons recurrence entirely...

The attention mechanism allows the model to ==weigh the relevance of every
other word when encoding a given word, regardless of distance==.

> [!note]
> This is what makes transformers better than RNNs for long-range dependencies

Transformers require no recurrence and no convolution...
```

### How the LLM processes this format

| Element | How it appears | LLM handling |
|---------|---------------|--------------|
| YAML frontmatter | Top of file | Parsed for `title`, `source_url`, `author`, `source_date` |
| `==text==` highlights | Inline in body | Treated as high-weight content — primary synthesis material |
| `> [!note]` callouts | Block annotations | Filed under "Open Questions" — not treated as source facts |
| `![[image.png]]` | Local image embeds | Ignored — paths don't resolve outside the vault |
| Frontmatter `tags` | In YAML block | Informational — LLM may use to suggest `domain:` tags |

---

## Keeping Track of What Has Been Processed

The LLM tracks processed sources via the `source_file:` frontmatter field in wiki pages — it will skip files already referenced there.

**Do not rename files** after they have been copied into `sources/obsidian-exports/`. The filename is the stable identifier.

The sync script stores a cursor in `sources/obsidian-exports/.last_sync` (gitignored) so it knows which files are new on each run.
