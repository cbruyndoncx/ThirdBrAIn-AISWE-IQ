# 4.3.1 — marketing-cli@0.5.4 sync

## Summary

`ai-agent-skills 4.3.1` brings the bundled marketing pack in line with the upstream `marketing-cli@0.5.4` release.

This is a catalog sync, not a feature release. The CLI, TUI, and library-manager surface are unchanged from 4.3.0 — only the cataloged upstream entries and supporting metadata move.

## Highlights

- **Marketing pack is back in sync with upstream.** The `mktg` collection now ships 51 skills, matching the canonical `marketing-cli` skills manifest at `0.5.4`.
- **Five new cataloged upstream skills.** `mktg-setup` (first-run conversational setup wizard), `postiz` (scheduling for LinkedIn, Reddit, Bluesky, Mastodon, Threads, and 25+ other providers), `mktg-x` (authenticated X/Twitter reader), `firecrawl` (web scraping and search via the Firecrawl CLI), and `summarize` (text TL;DR via the `steipete/summarize` CLI).
- **Source rename completes.** Catalog metadata, install sources, and source URLs now point at `MoizIbnYousaf/marketing-cli` instead of the older `MoizIbnYousaf/mktg` path.

## What Changed

### Catalog

- Synced 51 marketing-cli skills against `marketing-cli@0.5.4`
- Added `mktg-setup`, `postiz`, `mktg-x`, `firecrawl`, and `summarize` as cataloged upstream entries on the `marketing` shelf
- Updated the `mktg` collection skill list to include the five new skills
- Refreshed `total`, `updated`, and source URLs in `skills.json`

### Docs

- Regenerated README library stats and `WORK_AREAS.md` from the synced catalog
- Updated the `What's New` section and the changelog entry for 4.3.1

## Why This Is Patch, Not Minor

The CLI and TUI are unchanged. Adding cataloged upstream entries does not introduce new commands, change install behavior, or break workspace state. Anyone tracking 4.3.x will get the new skills the next time they install or sync from the bundled library.
