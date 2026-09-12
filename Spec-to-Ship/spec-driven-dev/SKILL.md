---
name: spec-driven-dev
description: >
  Spec-Driven Development protocol that runs before every new project or major feature.
  Creates structured, LLM-optimized specifications that enable one-shot implementation.
  Guides through 4 sequential phases: Specify, Plan, Tasks, Implement. Detects when specs
  are needed vs. when to just build. After spec creation, identifies and installs required
  tools and MCPs. Use when: "new project", "build me an app", "I want to create",
  "spec this out", "let's spec", "start a new project", "build a spec", "one-shot this",
  "new feature", "add a feature", "build a feature", "I want to build", "I want to add",
  "major feature", "big feature", "implement a feature", "add X to the project".
  MUST trigger proactively when Claude detects a request that would touch 5+ files, introduce
  new data models or APIs, or require significant new functionality — even if the user does
  not explicitly mention specs or SDD. Do NOT start implementing multi-file features without
  running this skill first. If in doubt about scope, run Phase 0 (Scope Check) to decide.
---

<role>
Spec-Driven Development Protocol — the gateway that runs before every new project or major
feature to create the specifications that enable one-shot implementation.

**Core Philosophy**: Code is a lossy projection of specifications. Intent, constraints,
invariants, and architectural decisions must be captured in the spec BEFORE any code is
written. The spec is the product; the code is a byproduct.

**Sub-Skills**

| Component | Purpose |
|-----------|---------|
| retrofit | Pre-Phase 1: Scan existing project, build BASELINE.md for context |
| specifier | Phase 1: Gather requirements, business logic, user journeys → SPEC.md |
| architect | Phase 2: Technical architecture, data models, API contracts → PLAN.md |
| decomposer | Phase 3: Break plan into atomic, implementable tasks → TASKS.md |
| toolchain | Post-spec: Discover, install, and configure required tools/MCPs |
| sync | Post-spec: Push tasks to GitHub Projects, SPEC.md to Linear, configure sync |

**Dependency Chain**:
- Greenfield: specifier → architect → decomposer → toolchain → sync → implement
- Existing project: retrofit → specifier → architect → decomposer → toolchain → sync → implement
</role>

<context>
**The Problem**: Without a spec, Claude Code operates on incomplete context. It makes
assumptions about architecture, skips edge cases, and produces code that requires multiple
rounds of revision. Each revision degrades context window efficiency and compounds drift.

**The Solution**: Front-load ALL thinking into structured specification documents. When the
spec is comprehensive and LLM-optimized, implementation becomes mechanical execution —
one-shot or close to it.

**When FULL SDD is Required**:
- New projects (any greenfield work)
- Major features (touching 5+ files or introducing new architectural patterns)
- Significant refactors (changing data models, API contracts, or system boundaries)
- Any work the user explicitly wants to one-shot

**When LIGHT SDD Suffices**:
- Medium features (3-5 files, clear scope, known patterns)
- Features within an existing well-spec'd project

**When NO SDD is Needed**:
- Bug fixes (unless systemic)
- Small features (1-3 files, clear scope)
- Documentation, configuration, or styling changes

**Maturity Levels** (for user awareness, not skill configuration):
1. **Spec-first**: Spec written, used to guide implementation, then archived
2. **Spec-anchored**: Spec kept alive for ongoing evolution and maintenance
3. **Spec-as-source**: Spec is the only human-edited artifact; code is fully generated
</context>

<instructions>
Execute phases sequentially. Each phase produces a specific output document.
Do NOT proceed to the next phase until the current phase's output is reviewed and
approved by the user.

<phase id="0" name="Scope Check">
Before running the full SDD protocol, determine scope AND project state.

```
STEP 1: Detect project state

CHECK for existing project indicators:
  - package.json, requirements.txt, Cargo.toml, go.mod (package manifest)
  - .git directory with history
  - src/ or app/ directory with code
  - CLAUDE.md or build log
  - specs/BASELINE.md (already retrofitted)

IF existing project detected AND specs/BASELINE.md does NOT exist:
  project_state = EXISTING_NO_BASELINE
ELIF existing project detected AND specs/BASELINE.md EXISTS:
  project_state = EXISTING_WITH_BASELINE
ELSE:
  project_state = GREENFIELD

STEP 2: Determine scope

IF request matches ANY:
  - Keywords: "new project", "build me", "create an app/site/tool/platform"
  - Keywords: "I want to build", "let's build", "start a new"
  - Keywords: "new feature", "add a feature", "build a feature", "implement"
  - Keywords: "I want to add", "add X to", "build X for", "create X in"
  - Keywords: "spec this", "write a spec", "one-shot this"
  - Keywords: "deploy SDD", "add spec-driven", "retrofit", "baseline this"
  - Estimated scope: > 5 files or > 500 lines of new code
  - Introduces new data models, APIs, or architectural patterns
  - User explicitly requests SDD
  - User describes a feature that sounds non-trivial (multiple components,
    database changes, new API endpoints, new pages/routes)
THEN:
  scope = FULL_SDD

ELIF request is medium scope (3-5 files, clear patterns):
  scope = LIGHT_SDD
  RESPOND:
    "This is medium-sized. I'll do a lightweight spec — just enough to
     one-shot it cleanly."
  Execute abbreviated flow:
    - Ask 3-5 clarifying questions about scope, constraints, edge cases
    - Produce mini-spec inline (not a separate file)
    - Proceed to implementation
  EXIT

ELSE:
  scope = NO_SDD
  Proceed with normal implementation
  EXIT

STEP 3: Route based on project state + scope

IF scope == FULL_SDD AND project_state == EXISTING_NO_BASELINE:
  RESPOND:
    "This is an existing project without a baseline. Before we spec new work,
     I need to understand what's already built.

     **I'll run the retrofit process first:**
     - Scan your codebase, build log, git history, and config
     - Create a BASELINE.md capturing your current architecture and state
     - Then we'll flow into the normal spec process for your new feature

     Let me start scanning."
  GOTO Phase 0.5 (Retrofit)

ELIF scope == FULL_SDD AND project_state == EXISTING_WITH_BASELINE:
  RESPOND:
    "I see this project already has a baseline. I'll reference it for context
     as we spec your new work.

     **4 Phases:**
     1. **Specify** — What are we building and why?
     2. **Plan** — How will it be built technically?
     3. **Tasks** — What are the atomic units of work?
     4. **Implement** — Execute against the spec.

     Let's start with Phase 1."
  READ specs/BASELINE.md into context
  GOTO Phase 1

ELIF scope == FULL_SDD AND project_state == GREENFIELD:
  RESPOND:
    "This needs a spec before we build. I'm going to walk you through
     spec-driven development — this is where the real work happens.
     Once the spec is solid, implementation should be close to one-shot.

     **4 Phases:**
     1. **Specify** — What are we building and why?
     2. **Plan** — How will it be built technically?
     3. **Tasks** — What are the atomic units of work?
     4. **Implement** — Execute against the spec.

     Let's start with Phase 1."
  GOTO Phase 1
```
</phase>

<phase id="0.5" name="Retrofit (Existing Projects Only)">
Read `sub-skills/retrofit/SKILL.md` and execute the retrofit protocol.

**Input**: Existing project codebase
**Output**: `specs/BASELINE.md` in the project directory

**Gate**: User must validate the baseline assessment before proceeding.

```
AFTER retrofit completes:
  PRESENT: Summary of project state findings
  ASK: "Does this match your understanding of the project? Anything to correct?"

  IF user approves:
    ASK: "What do you want to build next for this project?"
    AWAIT: User's feature/work description
    GOTO Phase 1 (with BASELINE.md as context)
  ELSE:
    ITERATE on BASELINE.md based on corrections
    RE-PRESENT for approval
```
</phase>

<phase id="1" name="Specify (The What and Why)">
Read `sub-skills/specifier/SKILL.md` and execute the specification protocol.

**Input**: User's project idea, description, or requirements
**Output**: `specs/SPEC.md` in the project directory

**Gate**: User must review and approve SPEC.md before proceeding.

```
AFTER specifier completes:
  PRESENT: Summary of SPEC.md key points to user
  ASK: "Does this capture what you're building? Anything to add, change, or remove?"

  IF user approves:
    GOTO Phase 2
  ELSE:
    ITERATE on SPEC.md based on feedback
    RE-PRESENT for approval
```
</phase>

<phase id="2" name="Plan (The How)">
Read `sub-skills/architect/SKILL.md` and execute the planning protocol.

**Input**: Approved SPEC.md + user's tech stack preferences
**Output**: `specs/PLAN.md` in the project directory

**Gate**: User must review and approve PLAN.md before proceeding.

```
AFTER architect completes:
  PRESENT: Summary of PLAN.md — tech stack, architecture, key decisions
  ASK: "Does this technical approach look right? Any preferences or constraints
        I should know about?"

  IF user approves:
    GOTO Phase 3
  ELSE:
    ITERATE on PLAN.md based on feedback
    RE-PRESENT for approval
```
</phase>

<phase id="3" name="Tasks (The Decomposition)">
Read `sub-skills/decomposer/SKILL.md` and execute the task decomposition protocol.

**Input**: Approved SPEC.md + Approved PLAN.md
**Output**: `specs/TASKS.md` in the project directory

**Gate**: User must review and approve TASKS.md before proceeding.

```
AFTER decomposer completes:
  PRESENT: TASKS.md summary — task count, complexity distribution, execution order
  ASK: "Here's the breakdown. Ready to implement, or any adjustments needed?"

  IF user approves:
    GOTO Phase 3.5
  ELSE:
    ITERATE on TASKS.md based on feedback
    RE-PRESENT for approval
```
</phase>

<phase id="3.5" name="Toolchain Setup + Pre-Flight">
Read `sub-skills/toolchain/SKILL.md` and execute tool discovery protocol.

**Input**: Approved SPEC.md + PLAN.md + TASKS.md
**Output**: Tools installed + Pre-Flight Checklist for user

```
AFTER toolchain installs what it can:

  STEP 1: Tool Inventory — enumerate ALL available tools in the current environment
    SCAN for:
      - Browser automation: Playwright MCP, Chrome MCP (claude-in-chrome)
      - Database tools: Supabase MCP, Convex MCP, direct DB CLI
      - Deployment tools: Vercel MCP, Netlify CLI, etc.
      - Code execution: IDE MCP, Bash, Node/Python REPL
      - Project management: Linear MCP, GitHub CLI
      - Any other MCP servers available in the session

    FOR each available tool:
      DETERMINE: Will this tool be needed during implementation?
      IF yes: Add to REQUIRED_TOOLS list with specific use case
        (e.g., "Chrome MCP → verify user flows after each feature task")
        (e.g., "Supabase MCP → run migrations, verify schema, check data")

  STEP 2: Pre-Flight Checklist — tell the user EVERYTHING needed upfront
    PRESENT:
      "## Pre-Flight Checklist

      Before I start implementing, I need the following set up.
      Once everything is confirmed, I'll run autonomously — you can
      walk away and come back when I'm done.

      ### Tools I'll Be Using
      {list each tool from REQUIRED_TOOLS with what it's for}

      ### What I Need From You NOW
      {For each NEEDS_AUTH or MANUAL_SETUP item:}
      - [ ] {Specific action — e.g., "Open Supabase dashboard in Chrome and stay logged in"}
      - [ ] {Specific action — e.g., "Paste your Stripe API key into .env as STRIPE_KEY=xxx"}
      - [ ] {Specific action — e.g., "Keep this terminal session running — do not close it"}

      ### Browser Tabs to Keep Open
      {List specific URLs/services Claude will need to access via browser tools}
      - [ ] {e.g., "Supabase project dashboard (I'll run SQL and verify tables)"}
      - [ ] {e.g., "Vercel deployment dashboard (I'll check deploy status)"}
      - [ ] {e.g., "localhost:3000 (I'll navigate and test the UI after building)"}

      ### Credentials / Access I Need
      {List every credential, env var, or access requirement}
      - [ ] {e.g., "DATABASE_URL in .env"}
      - [ ] {e.g., "SUPABASE_SERVICE_ROLE_KEY in .env"}

      ---
      Confirm each item above. Once confirmed, I will NOT ask you
      to do anything else until implementation is complete."

  STEP 3: User confirms everything is ready
    AWAIT: User confirms all checklist items
    IF any item missing:
      Explain exactly what's blocked without it
      AWAIT: User resolves and confirms

  GOTO Phase 3.75
```
</phase>

<phase id="3.75" name="Project Sync (Optional)">
Read `sub-skills/sync/SKILL.md` and execute the sync protocol.

**Input**: Approved SPEC.md + PLAN.md + TASKS.md
**Output**: GitHub Project issues + Linear documents + sync configuration

```
ASK: "Do you want to push these tasks to GitHub Projects, Linear, or both?
      This lets you (and collaborators) track progress visually.
      You can also skip this and sync later."

IF user wants sync:
  Execute sync protocol
  AWAIT: Sync complete + any manual setup steps done

IF user skips:
  CONTINUE

GOTO Phase 4
```

**Note**: Sync can also be run independently after the fact by invoking the sync
sub-skill directly. It reads from the existing specs/ directory.
</phase>

<phase id="4" name="Implement (Autonomous Execution)">
Execute tasks from TASKS.md sequentially or in parallel as dependencies allow.
**This phase is fully autonomous. The user should not need to intervene.**

**Process**:
1. Read SPEC.md, PLAN.md, and TASKS.md into context
2. Generate or update the project's CLAUDE.md with:
   - Project purpose (1-2 lines)
   - Tech stack and build/test/lint commands
   - Architectural constraints and invariants from SPEC.md
   - Key file structure overview
   - Non-default conventions
   - **MUST include** a Development Protocol section that enforces SDD for future work:
     ```
     ## Development Protocol
     This project uses Spec-Driven Development. All new features and non-trivial
     changes (3+ files, new data models, new APIs, new pages) MUST use the
     /spec-driven-dev skill. Do not start implementing multi-file features without
     running SDD first. Bug fixes and small changes (1-2 files) can proceed normally.
     ```
     This ensures that future sessions in this project automatically trigger SDD
     when appropriate, even if the skill's trigger phrases don't perfectly match
     the user's request.
3. Create `llms.txt` at project root pointing to all spec documents:
   ```
   # Project Specs
   > Specification documents for LLM context

   ## Docs
   - [Specification](specs/SPEC.md): Product requirements and invariants
   - [Technical Plan](specs/PLAN.md): Architecture and implementation design
   - [Tasks](specs/TASKS.md): Atomic implementation tasks
   ```
4. Execute tasks in dependency order from TASKS.md
5. After each task: run relevant validation (tests, lint, type check)
6. After all tasks: run full validation suite

**Autonomous Execution Protocol**:
```
CRITICAL: During implementation, you are the engineer AND the QA team.
Do not ask the user to:
  - Run database migrations (use database MCP or CLI yourself)
  - Check if something is working (use browser tools yourself)
  - Verify deployments (navigate to the URL yourself)
  - Run commands (use Bash yourself)
  - Test the UI (use Playwright or Chrome MCP yourself)

FOR each task:
  1. IMPLEMENT the code changes
  2. RUN any necessary commands (migrations, builds, installs)
  3. VERIFY the task works:
     - Run tests programmatically
     - If it's user-facing: open it in the browser and check it
     - If it touches the database: query the database and verify the data
     - If it's an API: call the endpoint and check the response
  4. Only mark the task complete AFTER verification passes

IF you encounter an error or blocker:
  1. Try to resolve it yourself using available tools
  2. Check documentation (context7, web search)
  3. Try alternative approaches
  4. ONLY ask the user if the blocker truly requires human action
     (e.g., a third-party account the user hasn't created yet)
```

**Live Verification Protocol**:
```
After completing each FEATURE or INTEGRATION layer task that has UI:

  1. Start the dev server if not already running
  2. Open the browser (Playwright or Chrome MCP) to the relevant page
  3. Walk through the user journey defined in SPEC.md:
     - Navigate to the feature
     - Interact with it as a user would
     - Verify the happy path works end-to-end
     - Check at least one edge case
  4. If something doesn't work: fix it before moving to the next task
  5. Take a screenshot or capture the state as evidence

After ALL tasks complete:

  1. Run the full application
  2. Walk through EVERY user journey from SPEC.md in the browser
  3. Verify each invariant is enforced (not just in tests — in the live app)
  4. Check error states render correctly
  5. Produce a verification report:
     "## Verification Report
     | Journey | Status | Notes |
     |---------|--------|-------|
     | {journey 1} | PASS/FAIL | {details} |
     ..."
```

**Tool Usage Mandate**:
```
Before starting implementation, review the REQUIRED_TOOLS list from Pre-Flight.
For EACH tool, know exactly when you'll use it:

  Browser tools (Playwright / Chrome MCP):
    → After every UI-facing task: navigate and verify
    → Final verification: walk through all user journeys
    → When debugging: visually inspect what the user sees

  Database tools (Supabase MCP / Convex / direct CLI):
    → Run migrations and schema changes yourself
    → Verify data is being stored correctly after writes
    → Check indexes and constraints are applied

  Deployment tools (Vercel MCP / etc.):
    → Deploy preview builds after integration tasks
    → Verify deployment succeeded by navigating to URL

  Package/CLI tools:
    → Install dependencies as needed
    → Run build, test, lint commands yourself
    → Fix any failures before proceeding

DO NOT say "you can verify by running..." — YOU run it.
DO NOT say "open the browser and check..." — YOU open it.
DO NOT say "run this SQL..." — YOU run it.
```

**Self-Check**: After implementation, compare output against SPEC.md.
```
READ specs/SPEC.md
FOR each capability:
  CHECK: Is it implemented?
  CHECK: Do acceptance criteria pass?
  CHECK: Does it work in the live app? (verify via browser)

FOR each invariant:
  CHECK: Is it enforced in code?
  CHECK: Is it covered by tests?
  CHECK: Does it hold in the running application?

FOR each user journey:
  CHECK: Walk through it in the browser
  CHECK: Does the happy path complete successfully?
  CHECK: Are edge cases handled?

LIST any unaddressed items
IF unaddressed items exist:
  FIX THEM — do not present them to the user as "recommendations"
  Only flag items that genuinely require user decisions (business logic ambiguity)
```

**Validation**: See `references/validation-checklist.md` for the 6-pillar framework.
</phase>
</instructions>

<rules>
1. **Spec Before Code**: Never write implementation code before Phases 1-3 are complete and approved
2. **Human Gates**: Each phase requires explicit user approval before proceeding
3. **Sequential Phases**: No skipping phases (scope-appropriate shortcuts are handled by Phase 0)
4. **Living Documents**: If requirements change during implementation, update spec documents FIRST, then adjust tasks and code
5. **Markdown Only**: All spec documents use Markdown — token-efficient, LLM-parseable, hierarchical
6. **Atomic Tasks**: No task in TASKS.md should touch more than 3 files
7. **Invariants Are Sacred**: If an invariant from SPEC.md would be violated, stop and flag it
8. **Explicit Over Implicit**: State everything in specs; assume the implementing agent has no prior context
9. **Autonomous Execution**: NEVER ask the user to do something Claude can do itself. If a database schema needs to be run — run it. If a page needs to be checked — open it in the browser. If a deployment needs to be verified — navigate to the URL. The user should be able to hit enter and walk away.
10. **Use Every Available Tool**: During implementation, actively use browser automation (Playwright, Chrome MCP), database MCPs, deployment tools, and every other available tool. "Available but unused" is a failure state. If you can verify something with a tool, you MUST verify it with that tool.
11. **Verify Like a User**: After implementing any user-facing feature, test it from the user's perspective using browser tools. Navigate to the page. Click the buttons. Submit the forms. Check the results. Do not just check if code compiles — check if the experience works.
12. **Context Lock**: Once SDD is activated, ALL work in this session must operate within the SDD framework. Reference spec documents for every decision. Do not drift into ad-hoc implementation. If a bug fix or adjustment is needed mid-implementation, handle it within the SDD task structure (update TASKS.md if needed) rather than going off-script.
13. **Session Continuity**: If context window is filling up, proactively write `specs/SESSION_STATE.md` with current progress, then instruct the user on how to resume in a new session. A new session must be able to pick up exactly where the last one left off.
</rules>

<error_handling>
| Scenario | Action |
|----------|--------|
| User wants to skip spec | Explain value, offer LIGHT_SDD as compromise |
| Scope unclear | Ask clarifying questions before scope determination |
| Tech stack not specified | Propose based on requirements, await approval |
| Implementation diverges from spec | Stop, flag divergence, update spec or adjust code |
| Toolchain setup fails | Document manual workaround, continue with available tools |
| Requirements change mid-build | Update SPEC.md → PLAN.md → TASKS.md first, then resume |
| User returns after break | Re-read spec documents to restore full context |
| Tool exists but not being used | This is a bug. If a tool is available and relevant, USE IT |
| About to ask user to do something | STOP. Can you do this yourself with available tools? If yes, do it |
| Context window getting full | Write SESSION_STATE.md BEFORE running out (see Session Continuity) |
| Session drifting from SDD | Re-read SPEC.md and TASKS.md, re-anchor to current task |
</error_handling>

<session_continuity>
**Context Lock Protocol**:
```
Once SDD is activated (scope == FULL_SDD), the session is LOCKED to SDD mode.

EVERY response during implementation must:
  1. Reference the current task from TASKS.md
  2. Operate within the spec framework
  3. Use available tools rather than deferring to the user

IF the user asks for a quick fix or tangential change during SDD:
  - Handle it, but frame it within the task structure
  - If it's a bug in what you just built: fix it as part of the current task
  - If it's a new requirement: add it to TASKS.md, then implement
  - NEVER drift into ad-hoc mode — stay anchored to the spec

IF the conversation shifts away from SDD accidentally:
  - Re-read specs/SPEC.md, specs/PLAN.md, specs/TASKS.md
  - Identify where you left off
  - Resume from that point
```

**Session Handoff Protocol**:
```
WHEN context window is approaching capacity (you notice responses slowing,
  compression warnings, or you're deep into implementation):

  1. IMMEDIATELY write specs/SESSION_STATE.md:
     ```markdown
     # Session State — {timestamp}

     ## Current Phase
     Phase {N}: {name}

     ## Progress
     ### Completed Tasks
     - T001: {title} — DONE
     - T002: {title} — DONE

     ### Current Task
     - T003: {title} — IN PROGRESS
       - What's done: {specific progress}
       - What's remaining: {specific next steps}
       - Blockers: {any issues}

     ### Remaining Tasks
     - T004: {title} — NOT STARTED
     - T005: {title} — NOT STARTED

     ## Environment State
     - Dev server running: yes/no (command to restart: {command})
     - Database state: {current migration status}
     - Browser tabs needed: {list}
     - Environment variables set: {list what's configured}

     ## Resume Instructions
     1. Open this project in Claude Code
     2. Run: /spec-driven-dev
     3. Say: "Resume implementation from SESSION_STATE.md"
     4. Claude will read SESSION_STATE.md, SPEC.md, PLAN.md, TASKS.md
        and continue from T003
     ```

  2. Tell the user:
     "I'm approaching my context limit. I've saved my progress to
      specs/SESSION_STATE.md. To continue:
      1. Start a new Claude Code session in this project directory
      2. Run /spec-driven-dev
      3. Say 'Resume from session state'
      I'll pick up exactly where I left off at task T003."

WHEN resuming from SESSION_STATE.md:
  1. Read specs/SESSION_STATE.md
  2. Read specs/SPEC.md, specs/PLAN.md, specs/TASKS.md
  3. Verify environment state matches what's documented
  4. Resume from the current task's remaining work
  5. Delete SESSION_STATE.md after fully resuming (it's stale once you're back)
```
</session_continuity>

<examples>
**New Project (FULL_SDD)**:
> User: "I want to build an app where you scan food barcodes and check ingredients
>        against EU/Japan regulations"
> → Scope: FULL_SDD
> → Runs Phase 1-4 sequentially with approval gates
> → Output: specs/SPEC.md, specs/PLAN.md, specs/TASKS.md, then implementation

**Large Feature (FULL_SDD)**:
> User: "Add real-time collaboration to the document editor"
> → Scope: FULL_SDD (new architectural pattern: WebSockets, CRDT)
> → Full protocol with all phases

**Medium Feature (LIGHT_SDD)**:
> User: "Add a dark mode toggle with system preference detection"
> → Scope: LIGHT_SDD
> → Quick clarifying questions, mini-spec inline, implement

**Small Fix (NO_SDD)**:
> User: "The login button is misaligned on mobile"
> → Scope: NO_SDD
> → Just fix it

**Proactive Detection**:
> User: "Build me a dashboard with auth, team management, and analytics"
> → Claude detects: 3 major subsystems, new data models, multiple APIs
> → Scope: FULL_SDD
> → "This needs a spec before we build..."

**Existing Project — First Time SDD (Retrofit)**:
> User: Opens Weedl project. "I want to add a new feature to Weedl"
> → Claude detects: existing codebase, no BASELINE.md
> → Scope: FULL_SDD, State: EXISTING_NO_BASELINE
> → Runs retrofit first → BASELINE.md
> → Then asks "What do you want to build?" → normal SDD flow

**Existing Project — Already Retrofitted**:
> User: Opens ARIA project (already has specs/BASELINE.md). "Add voice commands"
> → Claude detects: existing codebase, BASELINE.md present
> → Scope: FULL_SDD, State: EXISTING_WITH_BASELINE
> → Reads BASELINE.md for context → starts at Phase 1

**Sync to GitHub Projects + Linear**:
> After TASKS.md is approved, user chooses "GitHub Projects + Linear"
> → Creates GitHub Project with issues from TASKS.md
> → Pushes SPEC.md to Linear as a document
> → Guides user through Linear ↔ GitHub bidirectional sync setup
</examples>
