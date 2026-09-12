# ai-agent-skills 4.0.0

`ai-agent-skills 4.0.0` turns the project from a curated library into a library manager.

The bundled library is still here. It is still the default experience. The difference is that the same package can now power a managed library of your own.

## Highlights

- Managed workspaces with `init-library`
- `add <source>` for bringing bundled picks, upstream repo skills, or house copies into your own library
- `sync [name]` as the main refresh verb, with `update` kept as an alias
- Dependency-aware installs with `requires` and `--no-deps`
- Installed-state visibility across the CLI and TUI
- A new `Installed` view and workspace onboarding in the terminal UI
- Authored workflow guides for the new library-building loop

## Commands and surface changes

- New: `init-library <name>`
- New: `add <source>`
- New: `build-docs`
- New primary verb: `sync [name]`
- Compatibility alias: `update [name]`
- New install flag: `--no-deps`
- New catalog field: `requires: string[]`
- New workspace marker: `.ai-agent-skills/config.json`

## What changed under the hood

- The CLI and TUI now resolve the active library from the current directory.
- Bundled mode stays the default outside a workspace.
- Workspace mode becomes the source of truth inside a managed library root.
- Catalog installs can expand dependencies in deterministic order.
- Installed-state indexing is shared across list/search/info/collections/TUI.

## Upgrade notes

- `update` still works, but `sync` is now the primary command in docs and help output.
- The npm tarball now ships workflow docs only from `docs/`.
- Existing bundled-library workflows stay intact.

## Quick flow

```bash
npx ai-agent-skills init-library my-library
cd my-library

npx ai-agent-skills add frontend-design --area frontend --branch Implementation --why "I want this on my shelf."
npx ai-agent-skills add anthropics/skills --skill webapp-testing --area workflow --branch Testing --why "I use this when I want browser-level checks in the workspace."
npx ai-agent-skills install frontend-design -p
npx ai-agent-skills sync frontend-design -p
npx ai-agent-skills build-docs
```
