# 4.0.0 Announcement Pack

## X Post

`ai-agent-skills 4.0.0` turns the project from a curated library into a library manager.

It still ships my bundled shelves by default.
Now it also lets you create a managed library of your own with:

- `init-library`
- `add`
- `sync`
- dependency-aware installs
- a better TUI with installed-state visibility

Bundled library stays. Self-curation is finally real.

## LinkedIn Post

I just shipped `ai-agent-skills 4.0.0`.

This is the first release where the project really becomes more than my own curated library.

The bundled library is still the default experience, but the package now works as a library manager too. You can start a managed workspace, add bundled picks or upstream skills into it, rebuild your docs, and manage installs with a real workflow.

What is new in `4.0.0`:

- managed workspaces with `init-library`
- `add <source>` for building your own shelves
- `sync [name]` as the main refresh command
- dependency-aware installs with `requires`
- installed-state visibility across the CLI and TUI
- a new Installed view and workspace onboarding in the terminal UI

This is the release where `ai-agent-skills` stops being only “my kept library” and starts becoming the tool for keeping yours too.
