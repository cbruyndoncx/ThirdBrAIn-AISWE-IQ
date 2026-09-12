# Refresh Installed Skills

Use `sync` to refresh installed skills.

One skill:

```bash
npx ai-agent-skills sync frontend-design
npx ai-agent-skills sync frontend-design -p
```

Everything in a scope:

```bash
npx ai-agent-skills sync --all
npx ai-agent-skills sync --all -p
```

`sync` follows the install metadata:

- bundled library picks refresh from the active library
- workspace picks refresh from the workspace they came from
- direct GitHub, git, and local installs refresh from their recorded source

Use `check` when you want a quick status pass before syncing.
