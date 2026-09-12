---
person: "{{person}}"
seat: "{{seat}}"
date: "{{date}}"
status: active          # active | reviewed | stale
quadrant_counts:
  love_great: 0         # Love It / Great At It — keep
  like_good: 0          # Like It / Good At It — delegate when possible
  not_like_good: 0      # Don't Like It / Good At It — delegate soon
  not_like_not_good: 0  # Don't Like It / Not Good At It — delegate immediately
delegation_progress:
  delegated: 0          # Tasks successfully delegated
  total: 0              # Total tasks marked for delegation (bottom two quadrants)
  percent: 0
last_reviewed: "{{date}}"
---

# {{person}} — Delegate and Elevate

**Seat:** {{seat}}
**Last Audit:** {{date}}
**Status:** Active

---

## Quadrant 1: Love It / Great At It

*Keep these. This is your highest and best use.*

| # | Task / Responsibility | Source |
|---|----------------------|--------|
| 1 | [Task] | [Seat role / other] |

---

## Quadrant 2: Like It / Good At It

*Delegate when possible. You're good at these but they're not your highest use.*

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|
| 1 | [Task] | [Seat role / other] | | |

---

## Quadrant 3: Don't Like It / Good At It

*Delegate soon. You're competent but draining energy on these.*

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|
| 1 | [Task] | [Seat role / other] | | |

---

## Quadrant 4: Don't Like It / Not Good At It

*Delegate immediately. These are bottlenecks and burnout risks.*

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|
| 1 | [Task] | [Seat role / other] | | |

---

## Delegation Plan

*Actions for delegating tasks from Quadrants 3 and 4 (and eventually Quadrant 2).*

| Task | Delegate To | Training Needed | Timeline | Status |
|------|-------------|----------------|----------|--------|
| [Task from Q3/Q4] | [Person] | [Yes/No — details] | [Date] | [ ] Not started |

---

## Audit History

- {{date}}: Initial Delegate and Elevate audit conducted
