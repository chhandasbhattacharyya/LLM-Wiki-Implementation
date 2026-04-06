# CLAUDE.md — LLM Wiki Schema

This file is the operating manual for your LLM agent. Read it fully at the start of every session before touching any other file.

---

## Purpose

This wiki is a personal knowledge base maintained by an LLM agent. Rather than re-deriving knowledge from raw sources every time a question is asked, the LLM incrementally builds and maintains a structured, interlinked collection of markdown files. Knowledge compounds: once synthesised, it is available instantly for future queries and cross-referencing.

The human curates sources and asks questions. The LLM handles extraction, synthesis, cross-referencing, and maintenance.

---

## Directory Map

```
LLM-Wiki-Implementation/
├── CLAUDE.md                        ← This file. Read first, always.
├── .gitignore
│
├── wiki/                            ← The living knowledge base (LLM-owned)
│   ├── index.md                     ← Master page registry + tag taxonomy
│   ├── log.md                       ← Append-only session log
│   ├── concepts/                    ← Evergreen conceptual knowledge
│   │   └── _template.md
│   ├── entities/                    ← People, orgs, tools, products, places
│   │   └── _template.md
│   ├── events/                      ← Time-bound happenings, decisions
│   │   └── _template.md
│   └── references/                  ← Summarised external sources & articles
│       └── _template.md
│
├── sources/                         ← Raw input material (human-owned, never edited by LLM)
│   ├── notion-exports/              ← Markdown exported from Notion pages
│   └── manual/                      ← Other raw text dropped in manually
│
└── scripts/
    └── notion-export-guide.md       ← How to export from Notion
```

**Key rule:** Nothing in `sources/` is ever edited or deleted by the LLM. It is read-only feedstock. The LLM owns everything inside `wiki/`.

---

## Frontmatter Schemas

Every wiki page must begin with a YAML frontmatter block. Use the `_template.md` in each subdirectory as the authoritative schema. The required keys per type are:

### `concepts/`
```yaml
---
title: ""
type: concept
tags: []          # must be from the canonical taxonomy in wiki/index.md
aliases: []       # other names this concept is known by
related: []       # paths to other wiki pages (e.g. wiki/entities/openai.md)
sources: []       # filenames from sources/ that informed this page
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

### `entities/`
```yaml
---
title: ""
type: entity
entity_kind: person | org | tool | product | place
tags: []
aliases: []
related: []
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

### `events/`
```yaml
---
title: ""
type: event
date: YYYY-MM-DD          # use YYYY-MM for month-level precision
date_end: YYYY-MM-DD      # optional, for ranges
tags: []
participants: []          # paths to entity pages
related: []
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

### `references/`
```yaml
---
title: ""
type: reference
source_title: ""          # original article/paper/page title
source_url: ""
source_date: YYYY-MM-DD
author: ""
tags: []
related: []
source_file: ""           # filename in sources/ this was generated from
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

---

## Ingest Workflow

**Trigger:** New files appear in `sources/notion-exports/` or `sources/manual/`.

Follow these steps in order:

1. Read this file (`CLAUDE.md`) fully.
2. Read `wiki/index.md` to load the current page registry and tag taxonomy into context.
3. Identify unprocessed sources: files in `sources/` whose filename does not yet appear in any wiki page's `sources:` or `source_file:` frontmatter field.
4. For each unprocessed source:
   - Read the full file.
   - If it is a Notion export, strip the top-level Notion property table (the key-value block at the very top of the export). It is workspace metadata, not knowledge.
   - Treat `> ` blockquotes that came from Notion callout blocks as user-highlighted content — weight them more heavily during synthesis.
   - Ignore broken image paths (Notion exports contain relative image paths that will not resolve). Only use alt-text if it contains substantive content.
   - Preserve any personal annotations or comments the user added to the Notion page body. File these under "Open Questions" or "Notes" in the wiki page — do not treat them as source facts.
   - Determine the primary knowledge type: concept, entity, event, or reference.
   - Check `wiki/index.md` for existing pages that overlap with this source. If a match exists, update that page rather than creating a new one.
   - Draft the new or updated wiki page using the appropriate `_template.md` as the schema.
   - Assign tags from the canonical taxonomy. If new tags are needed, add them to the taxonomy in `wiki/index.md` with a one-sentence definition before using them.
   - Add cross-references to existing wiki pages using the cross-reference convention below.
   - Write the page file to the correct subdirectory.
5. Update `wiki/index.md`: add new pages to the Page Registry, update the Tag Taxonomy, update `total_pages` and `last_updated`.
6. Append one entry to `wiki/log.md` for this session.

---

## Query Workflow

**Trigger:** User asks a question or requests a summary.

1. Read this file (`CLAUDE.md`).
2. Read `wiki/index.md` to identify candidate pages by tag or title match.
3. Read the identified pages in full.
4. Follow all `related:` cross-references one level deep — read those pages too.
5. Synthesise an answer from wiki content. Cite which pages you drew from (by path).
6. If the wiki lacks sufficient information, say so explicitly and suggest running Ingest on relevant sources.
7. If the query reveals a gap or inconsistency in the wiki, note it so the user can decide whether to run Ingest or a manual edit.
8. Only append to `wiki/log.md` if the query produced a wiki edit.

---

## Lint Workflow

**Trigger:** User requests a health check, or after every ~10 Ingest sessions.

1. Read this file (`CLAUDE.md`).
2. Read `wiki/index.md`.
3. Read every page in `wiki/` (all subdirectories, excluding `_template.md` files).
4. For each page check:
   - All required frontmatter keys are present and non-empty (compare against the schema above).
   - `updated:` date is not earlier than `created:` date.
   - All paths in `related:` and `participants:` actually exist as files in the repo.
   - All tags in the page appear in `wiki/index.md`'s Tag Taxonomy.
   - `sources:` / `source_file:` entries refer to files that exist in `sources/`.
   - Pages with no inbound `related:` references from other pages (orphans).
5. For each issue:
   - Fix it directly if the fix is unambiguous (e.g., add a missing tag to the taxonomy, correct a path typo).
   - Otherwise flag it clearly for the user to resolve.
6. Update the Orphan Watch section in `wiki/index.md`.
7. Append a Lint entry to `wiki/log.md`.

---

## Cross-Reference Conventions

### In page bodies
Use wikilink syntax with explicit path and display name:
```
[[wiki/concepts/machine-learning.md|Machine Learning]]
```
Format: `[[<path-from-repo-root>|<display-name>]]`

### In frontmatter arrays (`related:`, `participants:`)
Use bare paths only:
```yaml
related:
  - wiki/concepts/machine-learning.md
  - wiki/entities/openai.md
```

This lets the LLM traverse the graph programmatically via frontmatter while keeping body text readable.

### Aliases
If a source uses a term that matches an `aliases:` entry in an existing page, link to the canonical page rather than creating a duplicate. The Alias Index in `wiki/index.md` enables fast alias lookup without reading every page.

---

## Tagging Taxonomy

Tags must be drawn from the canonical list in `wiki/index.md`. Three namespaces:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `domain:` | Subject area | `domain:machine-learning` |
| `status:` | Editorial state | `status:stub`, `status:evergreen`, `status:needs-review` |
| `source:` | Provenance | `source:notion-clip`, `source:manual`, `source:paper` |

Rules:
- Every page carries **1–3** `domain:` tags, **exactly 1** `status:` tag, and **0 or more** `source:` tags.
- Tags are lowercase and hyphenated.
- A `domain:` tag must apply to at least 3 pages before it is considered stable. If fewer than 3 pages would use it, prefer a cross-reference instead.
- When creating a new `domain:` tag, add it to the Tag Taxonomy in `wiki/index.md` with a one-sentence definition before using it on any page.

---

## Log Entry Format

Append to `wiki/log.md` — never modify previous entries.

```markdown
## YYYY-MM-DD — <one-line summary of session>

- **Action**: Ingest | Query | Lint | Manual Edit
- **Sources processed**: <list of filenames, or "none">
- **Pages created**: <list of wiki paths, or "none">
- **Pages updated**: <list of wiki paths, or "none">
- **Tags added**: <list, or "none">
- **Notes**: <anomalies, ambiguities, or decisions made>
```

---

## Hard Constraints

The LLM must never:

- Edit, rename, or delete any file in `sources/`.
- Modify or delete any previous entry in `wiki/log.md`.
- Create a wiki page without a complete frontmatter block matching the schema for its type.
- Invent a `domain:` tag without first adding it to the Tag Taxonomy in `wiki/index.md`.
- Use a `related:` path that does not correspond to an existing file.
- Treat user annotations in Notion exports as source facts.
