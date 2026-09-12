---
name: ceos-clarity
description: Use when taking a Clarity Break — stepping back from day-to-day work for strategic thinking time
file-access: [data/clarity/, templates/clarity-break.md, data/vision.md, data/rocks/, data/scorecard/, data/issues/open/, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-clarity

Facilitate the Clarity Break — one of the Five Leadership Abilities in EOS and a core Traction tool. A Clarity Break is scheduled time to step away from day-to-day work and think strategically: "work ON the business, not IN it." Unlike structured EOS tools, the Clarity Break is intentionally unstructured — this skill provides just enough framework to make it habitual without over-formalizing it.

## When to Use

- "Clarity break" or "take a clarity break"
- "Step back and think about the business"
- "Strategic thinking time" or "work on the business"
- "I need to reflect on the business"
- "Review how things are going" (in a reflective, non-meeting context)
- "Log a clarity break" or "record my reflections"
- "Show clarity break history" or "what themes keep coming up?"

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/clarity/YYYY-MM-DD.md` | Clarity Break notes (one per session) |
| `data/vision.md` | V/TO for strategic context |
| `data/rocks/[quarter]/` | Current Rocks for progress context |
| `data/scorecard/weeks/` | Recent scorecard data for trend context |
| `data/issues/open/` | Open issues for awareness context |
| `templates/clarity-break.md` | Template for new Clarity Break files |
| `data/accountability.md` | Accountability Chart (org structure for strategic context) |

### File Naming

Clarity Break files use date-based naming: `YYYY-MM-DD.md`

If a file already exists for today's date (e.g., a second Clarity Break in the same day), append a numeric suffix: `YYYY-MM-DD-2.md`, `YYYY-MM-DD-3.md`, etc.

### YAML Frontmatter Schema

```yaml
date: "2026-02-14"
person: "brad"
duration: "45 min"       # How long the Clarity Break lasted (filled at end)
themes:                  # Key themes identified during reflection
  - hiring
  - product-market-fit
issues_identified:       # Issues to bring to the next L10
  - "Sales pipeline is too dependent on one channel"
```

## Process

### Mode: Start

Guide a live Clarity Break session — gathering business context, prompting reflection, and capturing insights.

#### Step 1: Setup

1. **Person**: Ask who is taking the Clarity Break. Default to the user if a solo session.
2. **Date**: Use today's date.
3. **Collision check**: If `data/clarity/YYYY-MM-DD.md` already exists, check for the next available suffix.
4. Create the file path but don't write yet — the file is written at the end.

#### Step 2: Gather Context (State of the Business)

Read current data to provide a strategic snapshot. Keep each section to 2-3 lines — this is context, not a report.

1. **V/TO check**: Read `data/vision.md`. Summarize the 1-Year Plan and current progress.
2. **Rock status**: Read `data/rocks/[current-quarter]/`. Count on_track vs off_track. List any off-track Rocks.
3. **Scorecard trends**: Read the 2-3 most recent files in `data/scorecard/weeks/`. Note any metrics consistently off-track.
4. **Open issues**: Read `data/issues/open/`. Count total open issues. List the 3-5 highest priority ones.
5. **Org structure**: Read `data/accountability.md`. Note any unfilled seats or gaps relevant to the reflection topics.

Present the summary:

```
State of the Business
━━━━━━━━━━━━━━━━━━━━━

1-Year Plan: [brief summary from V/TO]
Rocks: 4/6 on track (Q1 2026)
  Off track: Hire VP Sales, Partner Program
Scorecard: Revenue on track, NPS off track 3 weeks running
Open Issues: 8 total — top 3: [issue titles]
```

If any data source is missing (no vision.md, no rocks, etc.), note it gracefully: "No [data type] on file yet." and continue.

Ask: "Want to review any of this in detail before we start reflecting, or shall we dive in?"

#### Step 3: Reflection

Present the four Clarity Break questions, one at a time. Give the user space to think — don't rush through them.

1. **"What's working well?"** — Celebrate wins. What should we keep doing or do more of?
2. **"What's not working?"** — Be honest. What's broken, frustrating, or draining energy?
3. **"What's missing?"** — What are we not doing that we should be? Gaps in people, process, or strategy?
4. **"What needs to change?"** — If you could change one thing about the business right now, what would it be?

Record the user's responses under each question. Don't analyze or problem-solve during the reflection — the goal is to surface thoughts, not fix things yet.

#### Step 4: Issues and Actions

After the four reflection questions:

1. Ask: "Did any new issues surface that should go on the Issues list for the next L10?"
2. If yes, capture them in the `issues_identified` frontmatter list.
3. Mention: "You can create formal issue files for these using `ceos-ids` when you're ready."

#### Step 5: Themes

Review the notes and suggest 2-4 themes — recurring topics or categories that emerged during the reflection. Ask the user to confirm or adjust. Record in the `themes` frontmatter list.

#### Step 6: Wrap Up and Save

1. Ask how long the Clarity Break took (for `duration` frontmatter).
2. Show the complete file before writing.
3. Ask for any final edits.
4. Write to `data/clarity/YYYY-MM-DD.md`.
5. Remind: "Run `git commit` to save your Clarity Break notes."

---

### Mode: Log

Record a Clarity Break that already happened (retroactive logging).

#### Step 1: Collect Details

Ask for:
- **Date**: When did the Clarity Break happen? Default to today.
- **Person**: Who took it?
- **Duration**: How long was it?

#### Step 2: Capture Insights

Prompt for key reflections:
- "What were the main things on your mind?"
- "Any insights or realizations?"
- "Did any issues surface that should go to the next L10?"

Record responses in the markdown body.

#### Step 3: Themes and Issues

1. Suggest 2-4 themes based on the notes.
2. Capture any issues in `issues_identified`.
3. Mention `ceos-ids` for formal issue creation.

#### Step 4: Save

1. Show the complete file.
2. Write to `data/clarity/YYYY-MM-DD.md` (with collision handling).
3. Remind about git commit.

---

### Mode: History

Review past Clarity Break notes and identify recurring themes.

#### Step 1: Load Clarity Breaks

Read all files in `data/clarity/`. Parse the YAML frontmatter from each file.

If no files exist: "No Clarity Breaks recorded yet. Want to start one?"

#### Step 2: Filter (Optional)

If the user specifies a person or date range, filter accordingly. Otherwise show all.

#### Step 3: Display Summary

Show a chronological list:

```
Clarity Break History
━━━━━━━━━━━━━━━━━━━━━

2026-02-14  brad  (45 min)  Themes: hiring, product-market-fit
2026-02-07  brad  (30 min)  Themes: sales-pipeline, hiring
2026-01-31  brad  (60 min)  Themes: product-market-fit, team-culture
2026-01-24  daniel (45 min) Themes: operations, hiring

Total: 4 Clarity Breaks
```

#### Step 4: Recurring Themes

Scan the `themes` frontmatter across all Clarity Breaks. Identify themes that appear in 3 or more sessions:

```
Recurring Themes (3+ appearances)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  hiring: 3 times (Feb 14, Feb 7, Jan 24)
  product-market-fit: 2 times (Feb 14, Jan 31)
```

Flag recurring themes: "These themes keep coming up. Consider surfacing them as formal Issues via `ceos-ids` if they haven't been addressed."

#### Step 5: Deep Dive (Optional)

Offer: "Want to open a specific Clarity Break to review the full notes?"

If yes, read and display the full file content.

## Output Format

**Start mode:** State of the business summary, then guided reflection. Complete file shown at the end.
**Log mode:** Prompts for retroactive capture, then complete file shown.
**History mode:** Chronological summary table with recurring themes analysis.

## Guardrails

- **Don't over-structure the reflection.** The Clarity Break is intentionally unstructured thinking time. Present the four questions as prompts, not a rigid checklist. If the user wants to free-form write, let them.
- **Context is optional.** If the user says "just let me think" or "skip the context," go straight to the reflection questions. Not every Clarity Break needs a state-of-the-business review.
- **Don't solve problems during the Clarity Break.** The goal is to surface thoughts, not fix things. Problem-solving happens in the L10 via IDS. If the user starts problem-solving, gently redirect: "Great insight — want to capture that as an issue for the next L10?"
- **Don't auto-invoke skills.** When issues surface during a Clarity Break, mention that `ceos-ids` can create formal issue files, but let the user decide. Same for scorecard updates (`ceos-scorecard`) or rock status changes (`ceos-rocks`).
- **One file per session.** Each Clarity Break produces one file. Don't update previous Clarity Break files — if themes evolved, that's captured in the new file.
- **Sensitive data warning.** On first use, remind the user: "Clarity Break notes may contain candid strategic reflections and sensitive business assessments. Use a private repo."

## Integration Notes

### V/TO (ceos-vto)

- **Read:** `ceos-clarity` reads `data/vision.md` during Start mode to provide 1-Year Plan context for the strategic reflection. This grounds the Clarity Break in the company's declared direction.
- **Suggested flow:** If the Clarity Break reveals the V/TO needs updating, suggest: "Consider reviewing the V/TO with `ceos-vto`."

### Rocks (ceos-rocks)

- **Read:** `ceos-clarity` reads `data/rocks/[current-quarter]/` during Start mode to show Rock progress. Off-track Rocks often surface as reflection topics.
- **Suggested flow:** Rock status changes belong in `ceos-rocks`, not in Clarity Break notes.

### Scorecard (ceos-scorecard)

- **Read:** `ceos-clarity` reads recent files from `data/scorecard/weeks/` during Start mode to identify trending metrics. Persistent off-track numbers are natural Clarity Break topics.
- **Suggested flow:** Scorecard logging stays in `ceos-scorecard`.

### Issues (ceos-ids)

- **Read:** `ceos-clarity` reads `data/issues/open/` during Start mode to show the current issues landscape. Issues identified during a Clarity Break are captured in frontmatter but NOT automatically created as issue files.
- **Suggested flow:** After the Clarity Break, use `ceos-ids` to create formal issue files for anything worth tracking.

### L10 Meetings (ceos-l10)

- **Related:** Clarity Break insights are designed to feed into the next L10 meeting. Issues identified during a Clarity Break can be raised during the L10's IDS section.
- **Suggested flow:** Mention any unresolved Clarity Break issues during the L10. The L10 skill will surface them from `data/issues/open/` if they've been formally created.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-clarity` reads `data/accountability.md` during Start mode to surface org structure context — unfilled seats, responsibility gaps, or role misalignments that may be worth reflecting on.
- **Suggested flow:** If the Clarity Break reveals accountability gaps, suggest: "Consider reviewing the Accountability Chart with `ceos-accountability`."

### Write Principle

Only `ceos-clarity` writes to `data/clarity/`. Other skills do not reference Clarity Break notes directly — they are personal reflections, not operational data.
