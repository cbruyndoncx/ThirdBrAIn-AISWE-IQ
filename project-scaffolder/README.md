# Claude Code Project Scaffolder

[![Support me on Patreon](https://img.shields.io/badge/Patreon-Support%20my%20work-FF424D?style=flat&logo=patreon&logoColor=white)](https://www.patreon.com/AndersBjarby)

A meta-project for spinning up new Claude Code projects with well-structured `CLAUDE.md` files, custom slash commands, subagent configurations, and agent skills — following Anthropic's current best practices (progressive disclosure, "less is more", don't send an LLM to do a linter's job).

## What it does

- **Slash commands** (`.claude/commands/`) — `/project:scaffold` (interactive wizard), `/project:scaffold-react`, `/project:scaffold-python`, `/project:generate-claude-md`, `/project:create-subagent`, `/project:create-skill`
- **Project analyzer agent** (`.claude/agents/project-analyzer.md`) — inspects a codebase to inform scaffolding
- **Templates** (`templates/`) — ready-made `CLAUDE.md` files (minimal, react-typescript, python-api, fullstack), reusable agents (code-reviewer, debugger, researcher), commands (fix-issue, review, test-and-commit) and a skill template
- **Docs** (`docs/`) — best practices, agent patterns, and subagent/skill authoring guides
- **`project-setup` skill** — packages the setup workflow as a Claude Code skill

## Usage

Open this project in Claude Code and run a scaffolding command, e.g.:

```text
/project:scaffold          # interactive project setup wizard
/project:scaffold-react    # quick React/TypeScript project
/project:scaffold-python   # quick Python project
```

The scaffolder reads the authoritative Anthropic engineering docs (linked in `CLAUDE.md`) before generating configs so recommendations stay current.

## Tech

Claude Code configuration project — Markdown `CLAUDE.md`, slash commands, subagents, skills, and templates. No build step.
