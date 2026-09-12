# SPEC.md Template

Use this template when generating the project's `specs/SPEC.md`. Adapt sections to
fit the project — omit sections that don't apply, add sections that are needed.

---

```markdown
# {Project Name} — Specification

## Overview
- **Name**: {project_name}
- **One-liner**: {what it does in one sentence — elevator pitch}
- **Problem**: {what problem it solves, in the user's words}
- **Target User**: {who uses it, what context they're in when they use it}
- **Success Metric**: {the ONE measurable thing that proves this works}

## Core Capabilities

### {Capability 1 Name}
**User Story**: As a {user type}, I want to {action} so that {outcome}.

**Description**: {2-3 sentences on what this capability does}

**Acceptance Criteria**:
- [ ] {Specific, testable criterion — "User can X and sees Y"}
- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}

### {Capability 2 Name}
...repeat for each capability...

## User Journeys

### {Journey 1: Primary Happy Path}
**Entry Point**: {how user arrives — direct URL, click from dashboard, etc.}

1. User {action}
2. System {response}
3. User sees {outcome}
4. User {next action}
5. ...

**Edge Cases**:
- **Empty state**: {what happens when there's no data yet}
- **Maximum**: {what happens at limits — max items, file size, etc.}
- **Concurrent**: {what happens if two users do this simultaneously}

**Error States**:
- **{Error condition}**: User sees {error message}. Recovery: {how to fix it}.
- **{Error condition}**: ...

### {Journey 2: Secondary Flow}
...repeat for each journey...

## Invariants

Rules that must ALWAYS hold. Implementation MUST enforce these.
Testing MUST verify these.

- [ ] `INV-001`: {rule} — {why it matters}
- [ ] `INV-002`: {rule} — {why it matters}
- [ ] `INV-003`: {rule} — {why it matters}
...

## Scope

### In Scope (v1)
- {Feature/capability — be specific}
- {Feature/capability}
- ...

### Explicitly Out of Scope
- {Thing NOT being built} — {reason: deferred to v2 / not needed / too complex}
- {Thing NOT being built} — {reason}

### Assumptions
- {Platform assumption: e.g., "Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)"}
- {User assumption: e.g., "Users have basic smartphone literacy"}
- {Infrastructure assumption: e.g., "Deployed on Vercel, using edge functions"}

## Competitive Context
- **{Comparable 1}**: {what they do well} / {what they miss}
- **{Comparable 2}**: {what they do well} / {what they miss}
- **Differentiation**: {what makes this project different}

## Non-Functional Requirements

### Performance
- {Budget: e.g., "Initial page load < 2s on 3G"}
- {Budget: e.g., "API responses < 200ms p95"}

### Security
- {Requirement: e.g., "All data encrypted at rest and in transit"}
- {Requirement: e.g., "OWASP Top 10 compliance"}

### Accessibility
- {Standard: e.g., "WCAG 2.1 AA compliance"}

### Platform
- {Target: e.g., "Web: responsive, mobile-first"}
- {Target: e.g., "iOS 16+, Android 12+"}
```

---

## Template Usage Notes

- **Remove sections that don't apply**. A CLI tool doesn't need accessibility sections.
  A simple API doesn't need user journeys for UI flows.
- **Add sections as needed**. If the project has unique concerns (regulatory compliance,
  hardware integration, etc.), add appropriate sections.
- **Be ruthlessly specific**. "Good performance" is useless. "API responses < 200ms p95"
  is useful. An implementing agent needs numbers, not vibes.
- **Invariants are the most important section**. These become the mechanical verification
  criteria. If you can't write a test for an invariant, rewrite it until you can.
- **Out of scope is as important as in scope**. It prevents the implementing agent from
  building things you didn't ask for.
