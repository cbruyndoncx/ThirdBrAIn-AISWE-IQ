# PRD Builder

AI-native Product Requirements Document builder for new and existing products. Walks through structured discovery, market research, and generation phases to produce comprehensive PRDs aligned with a 7-section accelerator framework.

## What It Does

PRD Builder runs 4 sequential phases:

| Phase | What Happens |
|-------|-------------|
| **Discovery** | Scans your existing codebase (if any) + walks you through a structured interview about your product vision, target user, features, and business model |
| **Research** | Conducts web research on competitors, market context, and user patterns to ground your PRD in reality |
| **Generator** | Synthesizes everything into a complete PRD using a proven template with user stories, success metrics, and risk analysis |
| **Reviewer** | Pressure-tests the PRD from engineering, user, and product strategy perspectives — then iterates with you |

## Requirements

- **Claude Code** (CLI) or **Cowork** — this is a folder-based composite skill and requires Claude Code's skill system
- Claude Code is free to install: https://docs.anthropic.com/en/docs/claude-code
- This skill does **not** work with Claude Desktop (which uses a different instruction system)

## Installation

### Option A: Quick Install (copy the folder)

1. Download or clone this repo
2. Copy the `prd-builder` folder into your Claude commands directory:

```bash
cp -r prd-builder ~/.claude/commands/prd-builder
```

3. Open Claude Code in any project and type `/prd-builder` to run it

### Option B: One-liner (clone directly)

```bash
git clone https://github.com/mrtblount/Claude-Skills.git /tmp/Claude-Skills && cp -r /tmp/Claude-Skills/prd-builder ~/.claude/commands/prd-builder && rm -rf /tmp/Claude-Skills
```

### Option C: From a zip file

If someone shared the `.zip` in Slack:

1. Unzip the file
2. Move the `prd-builder` folder to `~/.claude/commands/`:

```bash
unzip prd-builder.zip -d ~/.claude/commands/
```

3. Open Claude Code and type `/prd-builder`

## How to Use

Once installed, open Claude Code in any project directory and say:

- `/prd-builder` — starts the guided PRD process
- "Create a PRD" — also triggers the skill
- "I need a PRD for my app" — natural language works too

The skill will detect whether you have an existing codebase or are starting from scratch, then guide you through the process with checkpoints at each phase.

## File Structure

```
prd-builder/
├── SKILL.md                          # Main skill (orchestrator)
├── README.md                         # This file
├── references/
│   └── prd-template.md               # 7-section PRD template
└── sub-skills/
    ├── discovery/SKILL.md            # Phase 1: Interview + codebase scan
    ├── researcher/SKILL.md           # Phase 2: Market & competitive research
    ├── generator/SKILL.md            # Phase 3: PRD generation
    └── reviewer/SKILL.md             # Phase 4: Review & refinement
```

## Output

The skill produces:
- `PRD.md` — your complete Product Requirements Document
- `_prd/discovery-notes.md` — raw interview and codebase context
- `_prd/research-notes.md` — market and competitive research
- `_prd/review-notes.md` — reviewer findings and resolutions

## License

MIT
