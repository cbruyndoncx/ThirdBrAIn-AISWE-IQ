# Trode

A macOS menu bar app that tracks Claude Code usage AND shows skill evaluation scores from Tessl.

## Quick Context

- **What**: Electron menu bar app (React + TypeScript)
- **Why**: Content marketing for Tessl via natural signup flow
- **Full Spec**: See `prompt.md` for everything

## Current State

- [x] Milestone 1: Scaffold Electron app
- [x] Milestone 2: Usage Panel UI
- [x] Milestone 3: Skills Scanner
- [x] Milestone 4: Tessl CLI Integration
- [x] Milestone 5: Demo Project + Polish

## Current Task

**Read `.claude/tasks/current/task.md` before doing any work.**

If no task exists in `current/`, move one from `backlog/`:
```bash
mv .claude/tasks/backlog/01-scaffold.md .claude/tasks/current/task.md
```

## Commands

```bash
cd app && npm install       # Install dependencies
cd app && npm start         # Run the app
cd app && npm run package   # Build .dmg

# With demo project
SKILLS_PROJECT_PATH=./demo-project npm start
```

## Key Decisions

1. **Electron + Vite + React** (not Swift)
2. **Shell out to `tessl` CLI** (not API)
3. **Hardcoded eval scores** as fallback
4. **Reference**: https://github.com/Iamshankhadeep/ccseva for usage parsing

## Working Guidelines

1. **Read the current task** before starting any work
2. **Follow the Definition of Done** - stop when all checkboxes complete
3. **Respect constraints** - don't add features not in the current task
4. **Test before done** - ensure `npm start` works
5. **One milestone at a time** - don't peek at backlog

## Project Structure

```
trode/
├── CLAUDE.md               # This file
├── prompt.md               # Full specification
├── .claude/tasks/          # Task management
│   ├── backlog/            # Planned tasks
│   ├── current/            # Active task
│   └── done/               # Completed tasks
├── app/                    # Electron app
└── demo-project/           # Demo with sample skills
```

## The Marketing Hook

> "Some of your skills might be making your agent worse"

The karpathy-guidelines skill has **-3.5 lift** - it actually hurts performance!
