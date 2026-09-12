# PRD Template

Use this template when generating the project's `PRD.md`. Adapt sections to
fit the product — omit sections that don't apply, add sections that are needed.

---

```markdown
# {Product Name} — Product Requirements Document

> {One-liner: what this product does in one sentence}

**Last Updated**: {date}
**Status**: Draft | In Review | Approved
**Author**: {name}

---

## 1. Overview & Purpose

### What We're Building
{2-3 sentences describing the product at a high level. What is it?
What category does it belong to? What form does it take (web app, mobile
app, API, Chrome extension, etc.)?}

### Why We're Building It
{The strategic rationale. What opportunity are we seizing? What pain are
we eliminating? How does this align with broader goals?}

### Why Now
{The timing argument. What market shift, technology change, regulatory
change, or user behavior change creates this window of opportunity?}

---

## 2. Problem Statement

### The Problem
{Describe the specific pain point in the user's words. Be concrete.
Include a real or representative example of someone experiencing this
problem. What are the consequences of the problem going unsolved?}

### How People Cope Today
{What alternatives, workarounds, or competitors do users currently rely on?
What's broken about each approach?}

| Current Solution | What Works | What's Broken |
|-----------------|------------|---------------|
| {solution 1} | {strength} | {weakness} |
| {solution 2} | {strength} | {weakness} |
| {manual workaround} | {strength} | {weakness} |

### Our Insight
{What do we understand about this problem that others don't? This is the
foundation of differentiation. It could be a user insight, a technology
insight, or a market insight.}

---

## 3. Target User

### Primary User
- **Who**: {specific role, not a demographic — "early-stage startup founder
  building their first product" not "entrepreneurs aged 25-40"}
- **Context**: {when and where they encounter the problem}
- **Current behavior**: {what they do today to cope}
- **Emotional state**: {what frustrates them, what they fear, what they want}
- **Technical comfort**: {relevant skill level}
- **AI comfort**: {if applicable — AI-native, AI-curious, or AI-skeptical}

### Secondary Users (if any)
{Brief description of other user types who interact with the product
but are not the primary focus of v1}

### Who This Is NOT For
{Explicitly call out users you are not targeting in v1 and why.
This prevents scope creep.}

---

## 4. User Stories

### Core Stories (Must-Have)

**{Story 1: Primary Value}**
As a {specific user}, I want to {specific action} so that {real outcome}.
- Acceptance: {what "done" looks like — specific, testable}

**{Story 2}**
As a {specific user}, I want to {specific action} so that {real outcome}.
- Acceptance: {what "done" looks like}

**{Story 3}**
...

### AI-Assisted Stories (if applicable)

**{AI Story 1}**
As a {specific user}, I want AI to {specific AI task} so that {time/effort saved}.
- Acceptance: {what "done" looks like, including accuracy expectations}

**{AI Guardrail Story}**
As a {specific user}, I want to {see why AI made a recommendation / override AI / flag an error} so that I can {trust the system / maintain control}.
- Acceptance: {what the guardrail looks like}

### Nice-to-Have Stories
{Stories for features that add value but aren't critical for v1}

---

## 5. Features & Functionality

### Must-Have (v1 Launch)

#### {Feature 1 Name}
- **What it does**: {plain English description}
- **Why it matters**: {traces back to problem statement}
- **User story**: {reference to story above}
- **Acceptance criteria**:
  - [ ] {specific, testable criterion}
  - [ ] {specific, testable criterion}
  - [ ] {specific, testable criterion}

#### {Feature 2 Name}
...

### Nice-to-Have (v1 if time allows)

#### {Feature Name}
- **What it does**: {description}
- **Why it matters**: {rationale}
- **Would we delay launch?**: No

### Future (v2+)

- {Feature} — {reason for deferral}
- {Feature} — {reason for deferral}

### Explicitly Out of Scope
- {Feature NOT being built} — {reason}
- {Feature NOT being built} — {reason}

---

## 6. AI Feature Specification (include ONLY if product uses AI)

### AI-Powered Features

#### {AI Feature 1}
- **Input**: {what data/context the AI receives}
- **Expected behavior**: {what the AI should do}
- **Output**: {what the user sees}
- **Fallback**: {what happens when AI fails, is unavailable, or gives bad output}
- **Confidence display**: {how certainty is communicated to user}
- **User override**: {how the user corrects or rejects AI output}

### Human-in-the-Loop
{Where humans review, override, or correct AI decisions. Be specific
about which decisions require human approval vs. which are fully automated.}

### Data Requirements
- **Training/source data**: {what data powers the AI}
- **Data ownership**: {who owns the data}
- **Privacy & compliance**: {GDPR, HIPAA, SOC2, or other requirements}
- **Data freshness**: {how current does the data need to be}

### Feedback Loops
{How user behavior feeds back to improve the AI over time.
Be specific about what signals are captured and how they're used.}

### Ethics & Guardrails
- **Content policies**: {what the AI must never do or say}
- **Bias considerations**: {known risks and mitigation}
- **Transparency**: {how users know they're interacting with AI}
- **Safety limits**: {rate limits, scope boundaries, escalation triggers}

---

## 7. Non-Functional Requirements

### Performance
- {Specific budget: e.g., "Page load < 2s on 3G connection"}
- {Specific budget: e.g., "API responses < 200ms p95"}
- {Specific budget: e.g., "AI response < 3s for 90% of queries"}

### Security
- {Requirement: e.g., "All data encrypted at rest and in transit"}
- {Requirement: e.g., "Authentication via OAuth 2.0"}
- {Requirement: e.g., "OWASP Top 10 compliance"}

### Scalability
- {Target: e.g., "Support 1,000 concurrent users at launch"}
- {Target: e.g., "Handle 10x traffic spike without degradation"}

### Accessibility
- {Standard: e.g., "WCAG 2.1 AA compliance"}

### Platform & Device Support
- {Target: e.g., "Web: responsive, mobile-first, Chrome/Safari/Firefox"}
- {Target: e.g., "Progressive Web App with offline support"}

---

## 8. Success Metrics

### Primary Metric (North Star)
- **Metric**: {the ONE number that defines success}
- **Target**: {specific number and timeframe}
- **Measurement**: {how it's tracked}

### Supporting Metrics

| Metric | Target | Timeframe | Why It Matters |
|--------|--------|-----------|----------------|
| {metric} | {target} | {timeframe} | {rationale} |
| {metric} | {target} | {timeframe} | {rationale} |
| {metric} | {target} | {timeframe} | {rationale} |

### AI-Specific Metrics (if applicable)

| Metric | Target | Measurement |
|--------|--------|-------------|
| AI task completion rate | {target}% | {how measured} |
| User override rate | < {target}% | {how measured} |
| Error/hallucination rate | < {target}% | {how measured} |
| Time saved per session | {target} min | {how measured} |

### Anti-Metrics (What We're NOT Optimizing For)
- {metric we're explicitly deprioritizing — and why}

---

## 9. Assumptions, Risks & Open Questions

### Assumptions
{Things we're treating as true but haven't fully validated}

| Assumption | Impact if Wrong | Validation Plan |
|-----------|-----------------|-----------------|
| {assumption} | {consequence} | {how to test it} |
| {assumption} | {consequence} | {how to test it} |

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| {risk} | High/Med/Low | High/Med/Low | {plan} |
| {risk} | High/Med/Low | High/Med/Low | {plan} |

### Open Questions
- {question that needs an answer before or during development}
- {question that needs user research}
- {question that needs technical investigation}

---

## 10. Competitive Context

### Landscape

| Competitor | Category | Strengths | Weaknesses | Our Advantage |
|-----------|----------|-----------|------------|---------------|
| {name} | Direct | {strengths} | {weaknesses} | {why we win} |
| {name} | Indirect | {strengths} | {weaknesses} | {why we win} |

### Differentiation
{1-2 sentences on what makes this product fundamentally different.
Not "better UI" — something structural.}

---

## Appendix

### Glossary
{Define any domain-specific terms the team needs to know}

### References
- {Link to customer discovery notes}
- {Link to competitive analysis}
- {Link to design mockups}
- {Link to technical spec (when created)}
```

---

## Template Usage Notes

- **Remove sections that don't apply**. If the product doesn't use AI, remove
  Section 6 entirely. If there's no competitive landscape, keep it brief.
- **Add sections as needed**. Regulatory products may need a compliance section.
  Marketplace products may need sections for each side of the market.
- **The problem statement is the most important section**. If it's weak,
  everything downstream is built on sand.
- **User stories should make you feel something**. If "As a user, I want to
  log in" is the best you've got, dig deeper.
- **Metrics must be measurable**. "Improve user satisfaction" is not a metric.
  "NPS score > 40 within 3 months of launch" is a metric.
- **Out of scope is as important as in scope**. It prevents the team from
  building things nobody asked for.
- **Open questions are a sign of honesty, not weakness**. Better to name
  what you don't know than to pretend you have all the answers.
