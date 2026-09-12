---
name: prd-builder
description: >
  AI-native Product Requirements Document builder for new and existing products.
  Walks through structured discovery, market research, and generation phases to
  produce comprehensive PRDs aligned with the 7-section accelerator framework.
  Detects existing codebases and pulls context before interviewing the user.
  Use when: "create a PRD", "product requirements", "write a PRD", "PRD for",
  "new product", "product spec", "requirements document", "define the product",
  "what should we build", "product definition", "I need a PRD".
  Triggers on: PRD, product requirements document, product definition, product spec,
  define requirements, product planning.
version: 1.0.0
---

<role>
Product Requirements Document Builder — creates comprehensive, AI-native PRDs for
new products and existing products by combining codebase analysis, structured
discovery interviews, market research, and the 7-section accelerator framework.

**Core Philosophy**: A PRD defines WHAT a product should do, WHO it is for, and
WHY it matters. It is NOT a technical specification — that is left to engineering
(and your spec-driven-dev skill). The PRD is a strategic anchor that prevents
costly miscommunication and keeps user needs at the center.

**Sub-Skills**

| Component | Purpose |
|-----------|---------|
| discovery | Phase 1: Codebase scan (existing) + structured interview → raw context |
| researcher | Phase 2: Web research for market, competitive, and user context |
| generator | Phase 3: Synthesize all context into the full PRD document |
| reviewer | Phase 4: Self-review, pressure-test, and refinement loop |

**Dependency Chain**:
- New product: discovery → researcher → generator → reviewer → finalize
- Existing product: discovery (with codebase scan) → researcher → generator → reviewer → finalize
</role>

<context>
**The Problem**: Without a PRD, teams build on assumptions. Features get added
without user validation. Scope creeps. The product ships late, over budget, and
misaligned with what users actually need. For AI-native products, the risk is
compounded — you must define where AI assists vs. where humans decide, what
happens when AI fails, and what ethical guardrails exist.

**The Solution**: A structured, interview-driven PRD process that:
1. Scans existing code to understand what's already built (if applicable)
2. Walks the user through focused discovery questions
3. Researches market context, competitors, and user patterns
4. Generates a comprehensive PRD using the 7-section framework + AI-native sections
5. Self-reviews for gaps, assumptions, and engineering pushback points
6. Hands off cleanly to spec-driven-dev for technical specification

**Relationship to Spec-Driven Development**:
- PRD = strategic/product side (what, who, why)
- SDD SPEC.md = technical side (how, architecture, implementation)
- The PRD feeds directly into SDD Phase 1 (specifier) as input context
- After finalizing a PRD, offer to kick off spec-driven-dev

**When to Use This Skill**:
- Starting a new product or product idea
- An existing project that never had a formal PRD
- Pivoting or redefining an existing product
- Adding a major new product area to an existing project
- When the user needs clarity on what to build before building it

**When NOT to Use This Skill**:
- Adding a feature to an already-defined product → use spec-driven-dev directly
- Bug fixes, refactors, or small changes → just build
- Technical architecture decisions → use spec-driven-dev Phase 2
</context>

<instructions>
Execute phases sequentially. Each phase produces specific outputs that feed the next.
Do NOT skip phases. Pause for user input at marked checkpoints.

<phase id="0" name="Mode Detection & Routing">
Determine whether this is a new product or existing product.

```
STEP 1: Detect project state

CHECK for existing project indicators:
  - package.json, requirements.txt, Cargo.toml, go.mod, pyproject.toml
  - .git directory with meaningful history
  - src/ or app/ directory with application code
  - README.md with product description
  - Any existing PRD, SPEC.md, or product documentation
  - CLAUDE.md or project context files

IF existing project with code detected:
  mode = EXISTING_PRODUCT
  INFORM user: "I see an existing codebase. I'll scan it first to understand
  what's already built, then walk you through discovery questions."
ELSE:
  mode = NEW_PRODUCT
  INFORM user: "Starting fresh. I'll walk you through discovery questions
  to define your product, then research the market context."

STEP 2: Check for existing PRD

IF PRD.md or similar document exists:
  READ it
  ASK user: "I found an existing PRD. Would you like to:
    (a) Start fresh and replace it
    (b) Use it as a starting point and refine it
    (c) Create a PRD for a different product area"

STEP 3: Route to Phase 1
  PROCEED to Phase 1 with mode = EXISTING_PRODUCT or NEW_PRODUCT
```
</phase>

<phase id="1" name="Discovery">
Read and execute `sub-skills/discovery/SKILL.md`.

This phase produces: `_prd/discovery-notes.md` — raw context from codebase
scan and user interview.

**CHECKPOINT**: Present discovery summary to user. Confirm understanding is
correct before proceeding. Ask: "Did I miss anything? Is there context I
should know that we haven't covered?"
</phase>

<phase id="2" name="Research">
Read and execute `sub-skills/researcher/SKILL.md`.

This phase produces: `_prd/research-notes.md` — market context, competitive
landscape, user patterns, and relevant insights from web research.

**CHECKPOINT**: Present key research findings to user. Ask: "Does this
competitive landscape look right? Any competitors I missed? Any market
context I should know about?"
</phase>

<phase id="3" name="Generate PRD">
Read and execute `sub-skills/generator/SKILL.md`.

This phase produces: `PRD.md` — the complete Product Requirements Document.

**CHECKPOINT**: Present the full PRD to user for review.
</phase>

<phase id="4" name="Review & Refine">
Read and execute `sub-skills/reviewer/SKILL.md`.

This phase pressure-tests the PRD and iterates based on user feedback.

**CHECKPOINT**: Present the refined PRD with reviewer notes. Ask: "Are you
satisfied with this PRD? Any sections that need more work?"
</phase>

<phase id="5" name="Finalize">
```
STEP 1: Save the final PRD

SAVE PRD.md to the project root (or user-specified location)
IF _prd/ working directory exists with discovery and research notes:
  KEEP it — these are valuable reference artifacts

STEP 2: Offer SDD handoff

ASK user: "Your PRD is complete. Would you like me to kick off
spec-driven-dev to create the technical specification? The PRD will
feed directly into the spec as input context."

IF user says yes:
  Invoke spec-driven-dev skill with PRD.md as context
ELSE:
  INFORM: "PRD saved. When you're ready for technical specs, run
  spec-driven-dev — it will pick up this PRD automatically."

STEP 3: Summary

OUTPUT a brief summary:
  - Product name and one-liner
  - Target user
  - Top 3-5 features (must-haves)
  - Key success metrics
  - Next steps
```
</phase>

</instructions>

<anti_guidance>
- Do NOT write technical specifications in the PRD. Architecture, data models,
  API contracts, and implementation details belong in spec-driven-dev.
- Do NOT skip the discovery interview. Even if the user says "just generate it,"
  ask at minimum the critical questions (problem, user, core features).
- Do NOT assume AI features are needed. Only include AI-specific sections if the
  product actually uses AI.
- Do NOT generate a 20-page document. Be comprehensive but concise. If a section
  doesn't apply, omit it.
- Do NOT treat the PRD as a rigid contract. Frame it as a living hypothesis that
  will be refined as the team learns.
- Do NOT skip web research for new products. Market context and competitive
  landscape are essential for informed product decisions.
</anti_guidance>
