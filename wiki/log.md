# Wiki Log

Append-only chronological record of all wiki sessions. Never edit or delete previous entries.

Entry format:
```
## YYYY-MM-DD — <one-line summary>

- **Action**: Ingest | Query | Lint | Manual Edit
- **Sources processed**: <list or "none">
- **Pages created**: <list of wiki paths or "none">
- **Pages updated**: <list of wiki paths or "none">
- **Tags added**: <list or "none">
- **Notes**: <anomalies, decisions, ambiguities>
```

---

## 2026-04-06 — Wiki initialised

- **Action**: Manual Edit
- **Sources processed**: none
- **Pages created**: wiki/index.md, wiki/log.md, wiki/concepts/_template.md, wiki/entities/_template.md, wiki/events/_template.md, wiki/references/_template.md
- **Pages updated**: none
- **Tags added**: status:stub, status:needs-review, status:evergreen, source:notion-clip, source:manual, source:paper
- **Notes**: Repository scaffolded from the LLM Wiki pattern (Karpathy/chhandasbhattacharyya). Notion used in place of Obsidian for source collection.

---

## 2026-04-06 — Switched source pipeline from Notion to Readwise Reader

- **Action**: Manual Edit
- **Sources processed**: none
- **Pages created**: none
- **Pages updated**: CLAUDE.md, wiki/index.md
- **Tags added**: source:readwise
- **Tags removed**: source:notion-clip, source:manual
- **Notes**: User will use Readwise Reader exclusively. Removed sources/notion-exports/ and sources/manual/; created sources/readwise-exports/. Updated Ingest workflow to parse Readwise export format (Metadata block, highlight blockquotes, Note: annotations). Replaced scripts/notion-export-guide.md with scripts/readwise-export-guide.md.

---

## 2026-04-13 — Switched source pipeline from Readwise to Obsidian Web Clipper

- **Action**: Manual Edit
- **Sources processed**: none
- **Pages created**: none
- **Pages updated**: CLAUDE.md, wiki/index.md
- **Tags added**: source:obsidian-clip
- **Tags removed**: source:readwise
- **Notes**: User stopped using Readwise (cost). Switched to Obsidian Web Clipper. Removed sources/readwise-exports/; created sources/obsidian-exports/. Updated Ingest workflow to parse Obsidian export format (YAML frontmatter, ==highlights==, callout annotations). Replaced readwise scripts with obsidian_sync.py and obsidian-export-guide.md.
