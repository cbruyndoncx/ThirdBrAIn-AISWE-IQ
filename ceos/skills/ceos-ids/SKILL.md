---
name: ceos-ids
description: Use when identifying, discussing, or solving issues using the EOS IDS process
file-access: [data/issues/, templates/issue.md]
tools-used: [Read, Write, Glob]
---

# ceos-ids

Run the IDS (Identify, Discuss, Solve) process — the EOS method for resolving issues systematically. Every issue gets a root cause, a focused discussion, and at least one To-Do with an owner and due date.

## When to Use

- "We have an issue" or "add to the issues list"
- "IDS this" or "let's identify discuss solve"
- "What are our open issues?" or "show the issues list"
- "Solve [issue]" or "discuss [issue]"
- "Close this issue" or "mark [issue] as solved"
- During L10 meetings when the IDS section begins
- Any time the team needs structured problem-solving

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/issues/open/` | Open issues awaiting resolution |
| `data/issues/solved/` | Resolved issues (archive) |
| `templates/issue.md` | Template for new issue files |

### Issue File Format

Each issue is a markdown file with YAML frontmatter:

```yaml
id: issue-001
title: "Slow customer onboarding"
priority: 1            # 1 (highest) - 5 (lowest)
category: process      # people | process | data | vision | traction
ids_stage: identified  # identified | discussed | solved
created: "2026-02-06"
```

**Priority levels:**
- `1` — Critical, solve first
- `2` — High, solve soon
- `3` — Medium, solve when time allows
- `4` — Low, solve if capacity allows
- `5` — Nice-to-have, backlog

**Categories (the 5 EOS issue types):**
- `people` — right person, right seat issues
- `process` — systems, workflows, efficiency
- `data` — metrics, reporting, information gaps
- `vision` — alignment with V/TO, Core Focus
- `traction` — execution, accountability, follow-through

**IDS stages:**
- `identified` — root cause found, not yet discussed
- `discussed` — perspectives captured, not yet solved
- `solved` — To-Dos created, file moved to `data/issues/solved/`

**File naming:** `issue-NNN-slug.md` where NNN is a zero-padded ID and slug is the title slugified.

## Process

### Mode: List Issues

When the user asks to see the issues list.

1. Read all files in `data/issues/open/`.
2. Parse frontmatter for priority, category, and IDS stage.
3. Display sorted by priority (1 first):

```
Open Issues (6 total):
━━━━━━━━━━━━━━━━━━━━
P1  issue-003  Slow customer onboarding     [process]  identified
P1  issue-007  Key account churning          [people]   discussed
P2  issue-001  Reporting gaps in dashboard   [data]     identified
P3  issue-005  Misaligned marketing spend    [vision]   identified
P4  issue-002  Office Wi-Fi unreliable       [process]  identified
P5  issue-008  Update team photo on website  [process]  identified
```

If no open issues exist: "No open issues. Nice work! Use 'ceos-ids' to create one when a new issue surfaces."

---

### Mode: Create Issue (Identify)

Use when a new issue surfaces.

#### Step 1: Name the Issue

Ask: "What's the issue? Give it a short title."

#### Step 2: Dig for Root Cause (5 Whys)

Don't accept the first answer at face value. The stated problem is usually a symptom.

Walk through the 5 Whys:
1. "Why is this happening?" → [answer]
2. "And why is that?" → [answer]
3. "What's causing that?" → [answer]
4. Continue until you reach a root cause (usually 3-5 rounds)

Record both the stated problem and the root cause.

#### Step 3: Classify

1. **Priority** — How urgent? (1/2/3/4/5)
2. **Category** — Which EOS type? (people/process/data/vision/traction)

If the user isn't sure about category, help with examples:
- "Is this about having the right people?" → people
- "Is this about how work gets done?" → process
- "Is this about missing information?" → data
- "Is this about our direction?" → vision
- "Is this about executing the plan?" → traction

#### Step 4: Generate the ID

Read existing issue files in `data/issues/open/` and `data/issues/solved/`. Find the highest `issue-NNN` ID across both directories and increment. If no files exist, start at `issue-001`.

#### Step 5: Write the File

Use `templates/issue.md` as the template. Fill in:
- Frontmatter: id, title, priority, category, ids_stage=identified, created=today
- Identify section: stated problem and root cause from 5 Whys

Write to `data/issues/open/issue-NNN-slug.md`.

Show the file before writing. Ask: "Create this issue?"

---

### Mode: Discuss

Use when an identified issue needs discussion (often during L10).

#### Step 1: Open the Issue

Read the issue file. Show the current Identify section.

#### Step 2: Capture Perspectives

For each participant:
- "What's your perspective on this?"
- Record each person's view in the Discuss section

Rules for discussion:
- Everyone speaks. No one dominates.
- Stay focused on this issue — no tangents.
- No solving yet — just understanding.

#### Step 3: Update the File

1. Update `ids_stage` to `discussed` in frontmatter
2. Fill in the Discuss section with perspectives
3. Show the diff, ask for approval, write

---

### Mode: Solve

Use when a discussed issue is ready for resolution.

#### Step 1: Open the Issue

Read the issue file. Show the Identify and Discuss sections for context.

#### Step 2: Determine the Solution

Ask: "What's the solve? What specific actions will resolve this?"

For each action:
1. **Action** — what needs to be done (specific and verifiable)
2. **Owner** — one person (not "the team")
3. **Due date** — when will this be done

#### Step 3: Validate

- At least one To-Do is required. An issue can't be "solved" without a concrete action.
- Each To-Do has an owner and due date.
- Due dates should be realistic (usually within 1-2 weeks).

#### Step 4: Update the File

1. Fill in the Solve section with the To-Do table
2. Update `ids_stage` to `solved` in frontmatter
3. Show the diff, ask for approval, write

#### Step 5: Move to Solved

After writing the solved issue:
1. Move the file from `data/issues/open/` to `data/issues/solved/`
2. Confirm: "Issue [title] moved to solved. To-Dos are now the owners' responsibility."

If the user wants to keep it in open until To-Dos are done, that's fine — the `ids_stage: solved` status still indicates the IDS process is complete.

---

### Mode: Full IDS (Inline)

Use during L10 meetings or when running all three stages back-to-back.

1. **Identify** — Run 5 Whys, classify
2. **Discuss** — Capture perspectives
3. **Solve** — Create To-Dos
4. **Close** — Move to solved

This is the same as the three modes above, just run sequentially on a single issue.

## Output Format

**List:** Priority-sorted table of open issues.
**Create:** Complete issue file with Identify section.
**Discuss:** Updated issue file with perspectives added.
**Solve:** Completed issue file with To-Do table, moved to solved directory.

## Guardrails

- **Always show diff before writing.** Never modify an issue file without showing the change and getting approval.
- **At least one To-Do to solve.** An issue without an action item isn't solved — it's just discussed. Push for a concrete next step.
- **One owner per To-Do.** Not "the team" or "everyone." One person is accountable.
- **Don't skip Identify.** The 5 Whys matter. The most common failure is solving the symptom instead of the root cause. Push past the first answer.
- **Respect the stages.** Don't jump to Solve without first Identifying and Discussing. The stages exist to prevent premature solutions.
- **ID uniqueness.** Check both `open/` and `solved/` directories when generating a new ID to avoid collisions.
- **File lifecycle.** Issues start in `data/issues/open/`, move to `data/issues/solved/` when the IDS process is complete. Don't delete issue files — solved issues are the audit trail.
- **Integrate with L10.** During L10 meetings, IDS is Section 6. The `ceos-l10` skill will surface the issues list — this skill handles the actual IDS work on individual issues.
- **Don't auto-invoke other skills.** Mention `ceos-l10`, `ceos-todos`, and `ceos-vto` when relevant, but let the user decide when to switch workflows.
- **Sensitive data warning.** On first use, remind the user: "Issues may contain sensitive business problems and personnel matters. Use a private repo."

## Integration Notes

### L10 Meetings (ceos-l10)

- **Read:** `ceos-l10` reads open issues from `data/issues/open/` during Section 6 (IDS) of the L10 meeting. The L10 skill surfaces the prioritized list; `ceos-ids` handles the actual Identify, Discuss, Solve work on individual issues.
- **Suggested flow:** New issues surfaced during L10 should be created via `ceos-ids` Create mode.

### To-Dos (ceos-todos)

- **Related:** When an issue is solved, the Solve step creates To-Dos with owners and due dates. These should be tracked in `data/todos/` via `ceos-todos` Create mode with `source: ids`.
- **Suggested flow:** After solving an issue, suggest: "Create To-Dos for these action items with `ceos-todos`."

### V/TO (ceos-vto)

- **Read:** Issues categorized as `vision` relate to V/TO alignment. When such issues are identified, reference `data/vision.md` for context on the company's Core Focus and strategic direction.

### Read-Only Principle

Other skills read `data/issues/` for reference. **Only `ceos-ids` writes to issue files.** This preserves a single source of truth for issue tracking and resolution.
