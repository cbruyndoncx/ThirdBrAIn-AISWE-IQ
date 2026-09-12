---
name: ceos-quarterly
description: Use when conducting, scheduling, or reviewing quarterly conversations between managers and direct reports
file-access: [data/conversations/, templates/quarterly-conversation.md, data/vision.md, data/accountability.md, data/rocks/, data/people/]
tools-used: [Read, Write, Glob]
---

# ceos-quarterly

Facilitate the EOS Quarterly Conversation — the formal quarterly check-in between each manager and their direct reports. This is a two-way conversation about alignment, role satisfaction, and obstacles — not a performance review. It follows a specific 5-point agenda.

## When to Use

- "Run quarterly conversation for [person]" or "quarterly check-in with [name]"
- "Schedule quarterly conversations" or "who needs a quarterly conversation?"
- "Review quarterly conversations" or "show conversation history for [person]"
- "Quarterly one-on-one" or "manager check-in"
- Any discussion about formal quarterly conversations between managers and direct reports

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/conversations/QUARTER/` | Conversation files by quarter (e.g., `data/conversations/2026-Q1/`) |
| `data/vision.md` | Source of Core Values (read-only — use ceos-vto to modify) |
| `data/accountability.md` | Source of seats, owners, and reporting structure |
| `data/rocks/QUARTER/` | Rock files for the quarter (read-only — use ceos-rocks to modify) |
| `data/people/` | People Analyzer evaluations (read-only — use ceos-people to modify) |
| `templates/quarterly-conversation.md` | Template for new conversation files |

### Conversation File Format

Each conversation is a markdown file at `data/conversations/YYYY-QN/firstname-lastname.md` with YAML frontmatter:

```yaml
person: "Brad Feld"
manager: "Daniel"
quarter: "2026-Q1"
date: "2026-03-15"
core_values_rating: 5       # count of + ratings out of total Core Values
gwc_status: pass             # pass | fail | evaluating
rocks_completion_rate: 80    # percentage (0-100) or null if no Rocks
```

**File naming:** `firstname-lastname.md` — lowercase, hyphenated. Matches the naming convention from `ceos-people`.

### Quarter Format

Quarters follow `YYYY-QN` format: `2026-Q1`, `2026-Q2`, `2026-Q3`, `2026-Q4`.

To determine the current quarter from today's date:
- Jan-Mar = Q1, Apr-Jun = Q2, Jul-Sep = Q3, Oct-Dec = Q4

### The 5-Point Agenda

| # | Section | Focus |
|---|---------|-------|
| 1 | Core Values Alignment | How are they living the Core Values? |
| 2 | GWC | Do they still Get it, Want it, have Capacity? |
| 3 | Rocks Review | How did their Rocks go this quarter? |
| 4 | Role Expectations | Are roles clear and being met? |
| 5 | Feedback Both Ways | What's working? What's not? What's needed? |

### Key EOS Principles

- **Every direct report gets one conversation per quarter.** This is not optional — it's part of the system.
- **Two-way conversation.** The direct report should talk as much as the manager. It's a dialogue, not a lecture.
- **Reference, don't re-evaluate.** Core Values and GWC reference the People Analyzer results — this isn't a fresh evaluation. Rock completion is discussed, not re-scored.
- **Document everything.** The conversation is recorded and kept for future reference. Git history is the audit trail.

## Process

### Mode: Facilitate

Use when conducting a quarterly conversation with a specific person.

#### Step 1: Setup

1. **Identify the person and manager.** Ask for the person's name if not provided. Ask who is conducting the conversation (the manager).

2. **Determine the quarter.** Default to the current quarter. If near a quarter boundary, ask: "This conversation is for which quarter?"

3. **Check for existing conversation.** Look for `data/conversations/YYYY-QN/firstname-lastname.md`.
   - **Exists:** Ask: "A conversation already exists for [person] in [quarter]. Open it to review, or start a new one?"
   - **New:** Continue with Step 2.

4. **Gather context.** Read these files (silently — don't dump raw data to the user):
   - `data/vision.md` — extract Core Values list
   - `data/accountability.md` — find the person's seat(s) and their manager
   - `data/rocks/QUARTER/` — find Rocks owned by this person
   - `data/people/firstname-lastname.md` — load People Analyzer evaluation if it exists

5. **Create the quarter directory** if it doesn't exist: `data/conversations/YYYY-QN/`

Display a brief preparation summary:

```
Quarterly Conversation — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Manager: [Manager Name]
Quarter: YYYY-QN
Seat: [From accountability.md]
Core Values: [List from vision.md]
Rocks this quarter: [Count] ([List titles])
People Analyzer: [Status from people/ file, or "No evaluation on file"]

Let's walk through the 5-point agenda.
```

#### Step 2: Section 1 — Core Values Alignment

Read Core Values from `data/vision.md`. Display them and ask the manager to discuss how the person is living each one.

If a People Analyzer evaluation exists (`data/people/firstname-lastname.md`), show the most recent ratings as a reference point:

```
People Analyzer reference (last evaluated: 2026-01-15):
  Integrity: +
  Innovation: +/-
  Transparency: +
```

For each Core Value, prompt: "How is [person] living **[Core Value]**? Rate: `+`, `+/-`, or `-`"

Record ratings in the conversation file. Calculate `core_values_rating` as the count of `+` ratings.

**Important:** This is a reference discussion, not a re-evaluation. If the ratings differ significantly from the People Analyzer, note it: "These ratings differ from the People Analyzer. Would you like to update the People Analyzer after this conversation?"

#### Step 3: Section 2 — GWC

Read the person's seat from `data/accountability.md`. For each seat they hold, ask:

1. **Get it?** "Does [person] truly understand the [seat] role?" (yes/no + notes)
2. **Want it?** "Does [person] genuinely want to do [seat] work?" (yes/no + notes)
3. **Capacity?** "Does [person] have the capacity to excel at [seat]?" (yes/no + notes)

Display the result:

```
GWC — [Person] as [Seat]:
  Get it:     ✓ Yes
  Want it:    ✓ Yes
  Capacity:   ✓ Yes

  Right seat? Yes
```

Set `gwc_status`:
- All three yes = `pass`
- Any no = `fail`
- Not yet discussed = `evaluating`

If GWC differs from the People Analyzer, note it for follow-up.

#### Step 4: Section 3 — Rocks Review

Read all Rocks from `data/rocks/QUARTER/` where `owner` matches the person.

If no Rocks found: Display "No Rocks assigned this quarter." Set `rocks_completion_rate: null`.

If Rocks exist, display:

```
Rocks — [Person], [Quarter]:
  Launch Beta Program: complete ✓
  Partner Outreach: on_track (2/3 milestones done)
  Redesign Onboarding: dropped ✗
```

Prompt: "How do you feel about your Rock performance this quarter? Any context on the results?"

Calculate `rocks_completion_rate`: `(complete / total) * 100`, rounded to nearest integer. Include only `complete` and `dropped` statuses in the calculation — ignore `on_track` and `off_track` (those are mid-quarter Rocks still in progress).

**Important:** Don't re-score Rocks here. Use the status from the Rock files. If the quarter hasn't ended yet and Rocks are still `on_track`/`off_track`, note: "Rocks are still in progress — final scoring happens at quarter end with ceos-rocks."

#### Step 5: Section 4 — Role Expectations

Prompt the manager and direct report to discuss:

1. **Clarity:** "Are the roles and responsibilities for the [seat] clearly defined?"
2. **Delivery:** "Is [person] meeting those expectations?"
3. **Gaps:** "Are there areas where expectations aren't being met — on either side?"

Record responses. This section is qualitative — no scoring.

#### Step 6: Section 5 — Feedback Both Ways

This is the most important section. Both sides share openly.

**Manager → Direct Report:**
- "What's working well about [person]'s performance?"
- "What needs improvement?"

**Direct Report → Manager:**
- "What's working well about your relationship with your manager?"
- "What do you need from your manager that you're not getting?"

Record both sides. Emphasize that this is a dialogue.

#### Step 7: Action Items

Ask: "What action items come out of this conversation?"

Record 1-3 specific, actionable items with owners.

#### Step 8: Save the Conversation

1. **Show the complete conversation file** before writing.
2. Ask: "Save this quarterly conversation?"
3. Write to `data/conversations/YYYY-QN/firstname-lastname.md`.
4. Update frontmatter: `core_values_rating`, `gwc_status`, `rocks_completion_rate`, `date`.
5. Remind: "Run `git commit` to save the conversation."

If the People Analyzer ratings differed, offer: "Would you like to update the People Analyzer for [person]? This would update `data/people/firstname-lastname.md`."

---

### Mode: Schedule

Use when planning which quarterly conversations need to happen.

#### Step 1: Determine the Quarter

Default to the current quarter. Ask if the user wants a different quarter.

#### Step 2: Read the Accountability Chart

Read `data/accountability.md` to identify:
- All filled seats (person + seat name)
- Reporting structure (who reports to whom)

If the file doesn't exist or has no structure: "No accountability chart found. Create one first with `ceos-vto` or manually at `data/accountability.md`."

#### Step 3: Check Existing Conversations

Read `data/conversations/YYYY-QN/` to find which conversations have already been completed this quarter.

#### Step 4: Generate the Schedule

Display a table of all needed conversations:

```
Quarterly Conversations — YYYY-QN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Manager    | Direct Report | Seat        | Status  | Date       |
|------------|---------------|-------------|---------|------------|
| Brad       | Sarah Chen    | Integrator  | ✓ Done  | 2026-03-10 |
| Brad       | Mike Torres   | VP Sales    | Pending |            |
| Brad       | Alex Kim      | VP Eng      | Pending |            |
| Sarah      | Jamie Lee     | Marketing   | Pending |            |

Progress: 1/4 conversations complete (25%)
```

**Edge cases:**
- **Empty seats:** Flag: "📋 [Seat Name] — empty seat (no conversation needed)"
- **Departed people:** If `data/people/firstname-lastname.md` has `departed: true`, flag: "⚠️ [Person] departed — skip conversation?"
- **Self-conversation (Visionary/Integrator):** Include with note: "Self-reflection conversation"
- **Person with multiple seats:** List once with all seats noted

#### Step 5: Offer to Start

Ask: "Would you like to start a conversation with someone from this list?"

If yes, transition to Facilitate mode for the chosen person.

---

### Mode: Review

Use when reviewing past quarterly conversations for a person or the full team.

#### Step 1: Determine Scope

Ask: "Review conversations for a specific person, or the full team?"

- **Specific person:** Ask for the name
- **Full team:** Show all conversations

Also ask for the quarter, or default to the current quarter. Offer: "Show current quarter, or all quarters?"

#### Step 2: Read Conversation Files

**For a specific person:** Read all files matching `data/conversations/*/firstname-lastname.md` across quarters.

**For the full team:** Read all files from `data/conversations/YYYY-QN/`.

If no files found: "No quarterly conversations found. Run a Facilitate conversation to get started."

#### Step 3: Display Summary

**For a specific person (across quarters):**

```
Quarterly Conversations — Brad Feld
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Quarter | Manager | CV Rating | GWC    | Rocks Rate | Date       |
|---------|---------|-----------|--------|------------|------------|
| 2026-Q1 | Daniel  | 5/5       | Pass   | 80%        | 2026-03-15 |
| 2025-Q4 | Daniel  | 4/5       | Pass   | 100%       | 2025-12-20 |
| 2025-Q3 | Daniel  | 4/5       | Pass   | 67%        | 2025-09-18 |

Trend: Core Values stable, Rock completion improving
```

**For the full team (one quarter):**

```
Quarterly Conversations — 2026-Q1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Person      | Manager | CV Rating | GWC    | Rocks Rate | Date       |
|-------------|---------|-----------|--------|------------|------------|
| Brad Feld   | Daniel  | 5/5       | Pass   | 80%        | 2026-03-15 |
| Sarah Chen  | Brad    | 4/5       | Pass   | 100%       | 2026-03-12 |
| Mike Torres | Brad    | 3/5       | Fail   | 50%        | 2026-03-14 |

Team summary: 2/3 GWC passing, average Rock rate 77%
```

#### Step 4: Drill Down

Ask: "Want to view the full conversation for anyone?"

If yes, read and display the complete conversation file.

#### Step 5: Flag Issues

Highlight:
- **GWC failures:** "⚠️ [Person] — GWC fail. Discuss at next L10."
- **Low Rock completion:** If below 80%: "📉 [Person] — Rock completion below 80%."
- **Stale conversations:** If current quarter has no conversation and > 60 days into the quarter: "📅 [Person] — no conversation yet this quarter."

## Output Format

**Facilitate:** Walk through each section with prompts. Show the complete file before saving.

**Schedule:** Table of all needed conversations with completion status.

**Review:** Summary table with key metrics. Offer drill-down.

## Guardrails

- **Always show the complete file before writing.** Never create or modify a conversation file without showing it and getting approval.
- **Core Values come from vision.md.** Always read Core Values from `data/vision.md` — never ask the user to list them.
- **Cross-reference, don't duplicate.** Read People Analyzer ratings and Rock scores from their source files. Don't ask the user to re-enter data that's already on file.
- **One conversation per person per quarter.** If a conversation already exists, warn before creating a second one. Allow it (sometimes conversations need to be re-done), but make sure it's intentional.
- **Quarterly cadence.** If no conversation has been conducted for a person in > 120 days, flag it in Schedule and Review modes: "📅 Overdue — last conversation was [date]."
- **Two-way conversation.** Always prompt for both manager and direct report feedback in Section 5. Don't let it become one-sided.
- **Reference, don't re-evaluate.** This conversation references People Analyzer and Rock data — it doesn't replace those tools. If the user wants to change a People Analyzer rating, point them to `ceos-people`.
- **Sensitive data warning.** On first use in a session, remind the user: "Quarterly conversations contain sensitive performance data. Ensure your CEOS repo is private."
- **Respect the agenda.** Walk through all 5 sections in order. Don't skip sections even if the user tries to rush — each one serves a purpose. But keep each section focused and time-efficient.
- **Don't auto-invoke skills.** When conversation results suggest updating the People Analyzer or creating an issue, offer the option but let the user decide. Say "Would you like to update the People Analyzer?" rather than doing it automatically.

## Integration Notes

### V/TO (ceos-vto)

- **Read:** `ceos-quarterly` reads Core Values from `data/vision.md` for the Core Values Alignment section (Section 1) of the conversation.

### People Analyzer (ceos-people)

- **Read:** `ceos-quarterly` reads People Analyzer evaluations from `data/people/` as reference points for Core Values and GWC discussions. If ratings differ significantly, the skill suggests updating via `ceos-people`.

### Rocks (ceos-rocks)

- **Read:** `ceos-quarterly` reads Rock files from `data/rocks/[quarter]/` to show the person's Rock status during Section 3 (Rocks Review). It does not modify Rock files.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-quarterly` reads `data/accountability.md` to identify the person's seat(s) and reporting structure for GWC evaluation and scheduling.

### To-Dos (ceos-todos)

- **Related:** Action items from quarterly conversations should be created as To-Dos via `ceos-todos` Create mode with `source: quarterly`.

### Write Principle

**Only `ceos-quarterly` writes to `data/conversations/`.** Other skills reference conversation data for context. The quarterly conversation file is the sole record of each manager-direct report check-in.
