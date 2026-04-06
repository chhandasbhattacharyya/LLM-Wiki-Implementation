---
last_updated: 2026-04-06
total_pages: 0
---

# Wiki Index

This file is the master catalog of the wiki. The LLM updates it at the end of every Ingest session and whenever pages are created or modified.

---

## Tag Taxonomy

Canonical list of all tags in use. The LLM must add new `domain:` tags here with a definition before using them on any page.

### `domain:` — Subject area tags

| Tag | Definition |
|-----|-----------|
| *(none yet — add here as domains emerge)* | |

### `status:` — Editorial state tags

| Tag | Definition |
|-----|-----------|
| `status:stub` | Page exists but content is minimal; needs expansion |
| `status:needs-review` | Content present but accuracy or completeness is uncertain |
| `status:evergreen` | Well-sourced, consistently maintained, considered stable |

### `source:` — Provenance tags

| Tag | Definition |
|-----|-----------|
| `source:notion-clip` | Knowledge derived from a Notion Web Clipper export |
| `source:manual` | Knowledge from manually written or pasted source material |
| `source:paper` | Knowledge derived from an academic paper or research report |

---

## Alias Index

Maps alternate names to canonical wiki page paths. Updated by the LLM during Ingest when aliases are discovered.

| Alias | Canonical Page |
|-------|---------------|
| *(none yet)* | |

---

## Page Registry

All wiki pages catalogued here. `_template.md` files are excluded.

| Title | Type | Tags | Updated | Path |
|-------|------|------|---------|------|
| *(no pages yet)* | | | | |

---

## Orphan Watch

Pages with no inbound `related:` references from other pages. Reviewed during Lint.

| Page | Created | Notes |
|------|---------|-------|
| *(none)* | | |
