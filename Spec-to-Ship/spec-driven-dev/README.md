# Spec-Driven Development

A Claude Code skill that front-loads all thinking into structured specification documents before writing a single line of code. The result: one-shot (or near one-shot) implementation of large features and small products.

## The Problem

Without a spec, AI coding agents operate on incomplete context. They guess at architecture, skip edge cases, and produce code that needs multiple revision rounds. Each revision burns tokens and compounds drift.

## The Solution

Spec-Driven Development (SDD) runs a structured 4-phase protocol **before** implementation begins. By the time code is written, every decision has already been made. Implementation becomes mechanical execution.

```
Specify  ->  Plan  ->  Tasks  ->  Implement
 (what)      (how)    (units)    (execute)
```

## How It Works

### Phase 0: Scope Check
Automatically determines if SDD is needed. Small bug fixes skip it entirely. Medium features get a lightweight inline spec. Large features or new projects trigger the full protocol.

### Phase 0.5: Retrofit (Existing Projects)
For existing codebases, scans the project to build a `BASELINE.md` capturing current architecture, tech stack, and conventions before speccing new work.

### Phase 1: Specify
Interactive requirements gathering. Produces `SPEC.md` covering business logic, user journeys, edge cases, success criteria, and invariants. Optimized for LLM consumption.

### Phase 2: Plan
Translates the approved spec into technical architecture. Produces `PLAN.md` with tech stack decisions, data models, API contracts, file structure, and architectural constraints.

### Phase 3: Tasks
Decomposes the plan into atomic, dependency-ordered tasks. Each task touches 1-3 files max and is independently testable. Produces `TASKS.md`.

### Phase 3.5: Toolchain + Pre-Flight
Inventories all available tools (browser automation, database MCPs, deployment tools) and presents a checklist of everything needed before autonomous execution begins.

### Phase 4: Implement
Executes tasks autonomously. Runs migrations, verifies in the browser, tests endpoints, and validates against the spec. The user can walk away and come back to a working build.

## Sub-Skills

| Sub-Skill | Phase | What It Does |
|-----------|-------|--------------|
| `retrofit` | 0.5 | Scans existing projects, builds BASELINE.md |
| `specifier` | 1 | Requirements gathering -> SPEC.md |
| `architect` | 2 | Technical architecture -> PLAN.md |
| `decomposer` | 3 | Task decomposition -> TASKS.md |
| `toolchain` | 3.5 | Tool discovery, installation, pre-flight checklist |
| `sync` | 3.75 | Push tasks to GitHub Projects / Linear |

## Output Files

All spec documents are written to a `specs/` directory in your project:

```
your-project/
  specs/
    BASELINE.md   # (existing projects only)
    SPEC.md       # Requirements and invariants
    PLAN.md       # Technical architecture
    TASKS.md      # Atomic implementation tasks
```

## Installation

Copy the `spec-driven-dev` folder into your Claude Code skills directory:

```bash
# Clone the repo
git clone https://github.com/mrtblount/Claude-Skills.git

# Copy the skill
cp -R Claude-Skills/spec-driven-dev ~/.claude/skills/spec-driven-dev
```

Or copy just the folder directly into `~/.claude/skills/`.

## Usage

SDD activates automatically when Claude detects a request that needs it (new projects, large features, multi-file changes). You can also invoke it explicitly:

- "Build me an app that..."
- "Add a feature to..."
- "Spec this out"
- "One-shot this"
- `/spec-driven-dev`

### When It Triggers

| Scope | Example | What Happens |
|-------|---------|--------------|
| **Full SDD** | "Build a dashboard with auth and analytics" | All 4 phases with approval gates |
| **Light SDD** | "Add dark mode with system preference detection" | Quick inline spec, then build |
| **No SDD** | "Fix the login button alignment" | Just builds normally |

## Key Principles

- **Spec before code** -- No implementation until the spec is approved
- **Human gates** -- Each phase requires your approval before proceeding
- **Autonomous execution** -- During implementation, Claude uses every available tool (browser, database, deployment) rather than asking you to verify things manually
- **Session continuity** -- If context runs out mid-build, progress is saved to `SESSION_STATE.md` so a new session picks up exactly where it left off
- **Invariants are sacred** -- If something in the spec would be violated, Claude stops and flags it

## License

MIT
