---
name: ceos-kickoff
description: Use when conducting Focus Day, Vision Building Day 1, or Vision Building Day 2 — the EOS implementation kickoff sequence
file-access: [data/meetings/kickoff/, templates/focus-day.md, templates/vb-day-1.md, templates/vb-day-2.md, data/vision.md, data/rocks/, data/scorecard/, data/issues/, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-kickoff

Facilitate the EOS implementation kickoff sequence — the three foundational sessions where a leadership team first implements EOS. Focus Day introduces the tools and establishes the foundation. Vision Building Day 1 defines the Vision component (Core Values, Core Focus, 10-Year Target, Marketing Strategy). Vision Building Day 2 completes the V/TO (3-Year Picture, 1-Year Plan, Rocks, Issues List). These are one-time sessions, distinct from the recurring L10 or quarterly/annual planning cycles.

## When to Use

- "Focus Day" or "run our Focus Day"
- "Vision Building Day" or "VB Day 1" or "VB Day 2"
- "Start EOS" or "implement EOS" or "kick off EOS"
- "First EOS session" or "EOS implementation"
- "We're starting EOS — what's first?"
- Any reference to the initial EOS implementation sequence

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `templates/focus-day.md` | Focus Day session template |
| `templates/vb-day-1.md` | Vision Building Day 1 template |
| `templates/vb-day-2.md` | Vision Building Day 2 template |
| `data/meetings/kickoff/` | Saved kickoff session files |
| `data/vision.md` | Current V/TO (read-only — use `ceos-vto` to modify) |
| `data/accountability.md` | Accountability Chart (read-only — use `ceos-accountability` to modify) |
| `data/rocks/` | Rock files (read-only — use `ceos-rocks` to create) |
| `data/scorecard/` | Scorecard data (read-only — use `ceos-scorecard` to update) |
| `data/issues/open/` | Open issues (read-only — use `ceos-ids` to manage) |

### Kickoff Sequence

The EOS implementation follows a specific cadence:

1. **Focus Day** — Day 1. Introduces all EOS tools, creates initial drafts. Typically a full-day session.
2. **Vision Building Day 1** — ~30 days later. Deep dive into the Vision component. Half to full day.
3. **Vision Building Day 2** — ~30 days after VB Day 1. Completes the V/TO, sets first formal Rocks. Half to full day.

After all three sessions, the company transitions into the regular EOS rhythm: weekly L10s, quarterly planning, annual planning.

### File Naming

- `focus-day-YYYY-MM-DD.md` — Focus Day session
- `vb-day-1-YYYY-MM-DD.md` — Vision Building Day 1
- `vb-day-2-YYYY-MM-DD.md` — Vision Building Day 2

All files are saved in `data/meetings/kickoff/`.

## Process

This skill has three modes. Ask which session the user wants to run.

---

### Mode 1: Focus Day

*The first full-day session when starting EOS.*

#### 1. Setup

1. Ask for the date (default: today) and attendees.
2. Check for existing Focus Day files: `glob data/meetings/kickoff/focus-day-*.md`.
   - If found, ask: "A Focus Day session already exists ([date]). Open to review, append notes, or start fresh?"
3. Check for existing V/TO: `read data/vision.md`.
   - If populated, note: "V/TO already has content. Focus Day typically runs when first starting EOS. Continue anyway?"
4. Read the template: `read templates/focus-day.md`.
5. Replace placeholders (date, attendees) and start the session.

#### 2. Welcome & EOS Overview

Walk through the Six Key Components of EOS:
- **Vision** — Get everyone on the same page
- **People** — Right people, right seats
- **Data** — Manage by a Scorecard, not feelings
- **Issues** — IDS (Identify, Discuss, Solve)
- **Process** — Document the core processes
- **Traction** — Rocks + Meeting Pulse

Capture team expectations and commitment notes.

#### 3. V/TO Introduction

This is a first pass — capture initial thoughts, not final decisions:
- Core Values brainstorm (3-7 candidates)
- Core Focus first draft (Purpose + Niche)
- 10-Year Target initial idea

Note: "These will be refined and finalized in Vision Building Days 1 and 2."

#### 4. Accountability Chart Draft

Guide the team through building the initial org structure:
1. Define major functions (seats) — focus on the structure, not the people
2. Assign 5 key roles per seat
3. Place people into seats — mark where "Right Person, Right Seat" evaluation is needed

If `data/accountability.md` already exists, read it and build on it.

#### 5. Initial Rocks Brainstorm

Brainstorm priorities for the current quarter:
1. Ask: "What quarter are we in?" (set the {{quarter}} placeholder)
2. Brainstorm 10-20 Rock candidates
3. Narrow to company's top 3-7
4. Assign owners

Note: "These Rocks are preliminary. They'll be formalized in VB Day 2 after the full vision is set."

#### 6. Scorecard Discussion

Introduce the weekly Scorecard concept:
1. Explain: "5-15 numbers that tell the health of your business at a glance"
2. Brainstorm initial metrics
3. Assign owners and set weekly goals

#### 7. L10 Preview

Introduce the Level 10 Meeting format:
1. Walk through the 7-section L10 agenda (5-5-5-5-5-60-5 minutes)
2. Schedule the first L10 meeting (day, time, location)

#### 8. Conclude & Save

1. Summarize key outcomes from each section.
2. Set dates for Vision Building Day 1 (~30 days) and Vision Building Day 2 (~60 days).
3. Capture immediate action items.
4. Show the complete file and get approval.
5. Save to `data/meetings/kickoff/focus-day-YYYY-MM-DD.md`.

Suggest: "Use `ceos-accountability` to formalize the Accountability Chart. Use `ceos-scorecard` to set up the formal Scorecard."

---

### Mode 2: Vision Building Day 1

*Deep dive into the Vision component of the V/TO. Typically ~30 days after Focus Day.*

#### 1. Setup

1. Ask for the date and attendees.
2. Check for prior Focus Day: `glob data/meetings/kickoff/focus-day-*.md`.
   - If not found, warn: "No Focus Day session found. VB Day 1 typically follows a Focus Day. Continue anyway?"
   - If found, read it for context (prior V/TO drafts, Core Values brainstorm, etc.).
3. Check for existing VB Day 1 files: `glob data/meetings/kickoff/vb-day-1-*.md`.
   - If found, ask: "A VB Day 1 session already exists ([date]). Open to review, append notes, or start fresh?"
4. Read the template: `read templates/vb-day-1.md`.
5. Replace placeholders and start.

#### 2. Core Values Definition

Guide the team through the Core Values discovery exercise:
1. **Speech exercise:** "If you had to give a speech about what makes [Company] great, who would you point to as the embodiment? Why?"
2. From the Focus Day brainstorm, refine to 3-7 final Core Values.
3. Define each value — one sentence that explains it in your company's language.
4. Add example behaviors for each value.
5. **People Filter Test:** Do these values help you hire, fire, and review?

#### 3. Core Focus Clarification

Finalize the two elements of Core Focus:
1. **Purpose / Cause / Passion:** Why does this organization exist beyond making money?
2. **Niche:** What do you do better than anyone else? What's your sweet spot?
3. Validation: Is it simple? Does it energize? Does it filter opportunities?

#### 4. 10-Year Target Setting

Set the one big goal:
1. Review the Focus Day draft if available.
2. Make it specific and measurable.
3. Gut check: Exciting? Measurable? Actually 10 years out?

#### 5. Marketing Strategy

Walk through the Four Marketing Strategy Uniques:
1. **Target Market:** Geographic, Demographic, Psychographic, The List (top 10-20 prospects)
2. **Three Uniques:** What combination of three things differentiates you from ALL competitors?
3. **Proven Process:** Name your process. Break it into 3-7 steps.
4. **Guarantee:** What brand promise can you make?

#### 6. Conclude & Save

1. Summarize decisions from each section.
2. Set date for Vision Building Day 2 (~30 days).
3. Assign pre-VB2 action items (share Core Values with team, test Marketing Strategy).
4. Show the complete file and get approval.
5. Save to `data/meetings/kickoff/vb-day-1-YYYY-MM-DD.md`.

Suggest: "Use `ceos-vto` to formalize the Vision component (Core Values, Core Focus, 10-Year Target, Marketing Strategy) into `data/vision.md`."

---

### Mode 3: Vision Building Day 2

*Complete the V/TO and set the first formal Rocks. Typically ~30 days after VB Day 1.*

#### 1. Setup

1. Ask for the date and attendees.
2. Check for prior VB Day 1: `glob data/meetings/kickoff/vb-day-1-*.md`.
   - If not found, warn: "No VB Day 1 session found. VB Day 2 typically follows VB Day 1. Continue anyway?"
   - If found, read it for context (Core Values, Core Focus, 10-Year Target, Marketing Strategy).
3. Also read the Focus Day file if available: `glob data/meetings/kickoff/focus-day-*.md`.
4. Check for existing VB Day 2 files: `glob data/meetings/kickoff/vb-day-2-*.md`.
   - If found, ask: "A VB Day 2 session already exists ([date]). Open to review, append notes, or start fresh?"
5. Read the template: `read templates/vb-day-2.md`.
6. Replace placeholders and start.

#### 2. 3-Year Picture

Paint a vivid picture of the company in 3 years:
1. Revenue, profit, headcount targets.
2. Narrative description: "What does the company look like? Culture? Products? Market position?"
3. 3-5 measurables with current state and 3-year targets.

#### 3. 1-Year Plan

Set specific goals for this year:
1. Revenue, profit, headcount targets for the year.
2. 3-7 goals that move toward the 3-Year Picture.
3. Each goal should be measurable with a clear owner.

#### 4. Quarterly Rocks Setting

Set the first formal Rocks:
1. Ask: "What quarter are we in?"
2. Set 3-7 company Rocks — each must be SMART (Specific, Measurable, Attainable, Realistic, Timely).
3. Set individual Rocks for each leadership team member (1-3 each).
4. **Alignment check:** Every Rock should connect to a 1-Year Goal.
5. Review the Focus Day Rock brainstorm — some may carry forward, others may have changed.

#### 5. Issues List Brainstorm

Surface all issues:
1. Brain dump — everything on everyone's mind. Quantity over quality.
2. Categorize by EOS component (Vision, People, Data, Issues, Process, Traction).
3. Prioritize (H/M/L) — but don't solve. Issues get worked through in L10 meetings.

#### 6. Conclude & Save

1. Summarize all V/TO sections and their completion status.
2. Review the V/TO completion checklist — all 8 sections should now have content.
3. Capture action items for formalizing decisions into CEOS data files.
4. Show the complete file and get approval.
5. Save to `data/meetings/kickoff/vb-day-2-YYYY-MM-DD.md`.

Suggest follow-up skills:
- "Use `ceos-vto` to formalize the complete V/TO into `data/vision.md`."
- "Use `ceos-rocks` to create formal Rock files in `data/rocks/`."
- "Use `ceos-ids` to enter issues into `data/issues/open/`."
- "Use `ceos-scorecard` to finalize Scorecard metrics."
- "Use `ceos-accountability` to finalize the Accountability Chart."

## Output Format

**During session:** Progressive display of each agenda section. Fill in the template section-by-section as the team works through it.

**Before saving:** Show the complete file content and get explicit approval before writing.

**File format:** Markdown with YAML frontmatter (date, attendees, location). Follows the template structure with tables for structured data and checklists for action items.

## Guardrails

- **Always show the complete file before writing.** Never create or modify a kickoff session file without showing it and getting approval.
- **Don't auto-invoke other skills.** Mention `ceos-vto`, `ceos-rocks`, `ceos-scorecard`, `ceos-ids`, `ceos-accountability`, and `ceos-l10` as follow-up tools, but let the user decide when to use them.
- **Kickoff captures decisions; component skills formalize them.** Never write directly to `data/vision.md`, `data/rocks/`, `data/accountability.md`, `data/scorecard/`, or `data/issues/`. Record decisions in the session file, then suggest the appropriate skill for formalization.
- **Warn on out-of-sequence sessions.** If VB Day 1 is run without a prior Focus Day, or VB Day 2 without VB Day 1, warn but allow. Some companies work with EOS Implementors who guide the process differently.
- **Don't enforce timing constraints.** Sessions are typically ~30 days apart, but don't block if they're closer or further apart.
- **Cross-reference existing data.** Read prior session files, V/TO, Rocks, and Accountability Chart when available. Build on what exists rather than starting from scratch.
- **Sensitive strategic data warning.** On first use in a session, remind the user: "Kickoff session notes contain sensitive strategic data. Ensure your CEOS repo is private."
- **All leadership must attend.** If the attendees list seems smaller than expected compared to `data/accountability.md`, note: "Some leadership team members may be missing from the attendee list."

## Integration Notes

### V/TO (ceos-vto)

- **Read:** `ceos-kickoff` reads `data/vision.md` to check if a V/TO already exists (Focus Day setup). VB Day 1 and VB Day 2 decisions are captured in session files, not written directly to the V/TO.
- **Suggest:** After VB Day 1 and VB Day 2, suggest using `ceos-vto` to formalize vision decisions into `data/vision.md`.

### Rocks (ceos-rocks)

- **Read:** `ceos-kickoff` reads `data/rocks/` to check for existing Rocks during setup. Focus Day brainstorms preliminary Rocks; VB Day 2 sets formal Rocks.
- **Suggest:** After VB Day 2, suggest using `ceos-rocks` to create formal Rock files.

### Scorecard (ceos-scorecard)

- **Read:** `ceos-kickoff` reads `data/scorecard/` to check for existing metrics. Focus Day introduces the Scorecard concept and brainstorms initial metrics.
- **Suggest:** After Focus Day, suggest using `ceos-scorecard` to formalize metrics.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-kickoff` reads `data/accountability.md` to check for existing chart during Focus Day. The Accountability Chart draft is captured in the Focus Day session file.
- **Suggest:** After Focus Day, suggest using `ceos-accountability` to formalize the chart.

### IDS (ceos-ids)

- **Read:** `ceos-kickoff` reads `data/issues/open/` to check for existing issues. VB Day 2 brainstorms the initial Issues List.
- **Suggest:** After VB Day 2, suggest using `ceos-ids` to enter issues.

### L10 (ceos-l10)

- **Reference:** Focus Day previews the L10 format and schedules the first L10. After the kickoff sequence is complete, the team transitions to the weekly L10 rhythm.
- **Suggest:** After Focus Day, suggest using `ceos-l10` to run the first Level 10 meeting.

### Orchestration Principle

`ceos-kickoff` is a one-time orchestrator for the EOS implementation sequence. Session files at `data/meetings/kickoff/` capture the leadership team's decisions; individual skills (`ceos-vto`, `ceos-rocks`, `ceos-scorecard`, `ceos-accountability`, `ceos-ids`) handle the formal data artifacts. The kickoff skill reads from many sources for context but writes only to its own directory.
