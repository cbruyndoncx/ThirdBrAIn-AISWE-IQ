# Validation Checklist

The 6 pillars of validation for spec-driven development. Use during and after
implementation to verify the build meets spec requirements.

---

## The 6 Pillars

### 1. Security
- [ ] No hardcoded secrets or API keys in codebase
- [ ] Input validation on all user-facing endpoints
- [ ] SQL injection prevention (parameterized queries or ORM)
- [ ] XSS prevention (output encoding, CSP headers)
- [ ] CSRF protection on state-changing operations
- [ ] Authentication on all protected routes
- [ ] Authorization checks (users can only access their own data)
- [ ] Dependency vulnerability scan clean (`npm audit` / `pip audit`)
- [ ] Sensitive data encrypted at rest and in transit
- [ ] Error messages don't leak internal details

### 2. Testing
- [ ] Unit tests for all business logic functions
- [ ] Integration tests for API endpoints
- [ ] E2E tests for critical user flows (at minimum: happy path)
- [ ] Edge case coverage (empty states, max limits, invalid input)
- [ ] All SPEC.md invariants verified by at least one test
- [ ] Test suite runs in CI and blocks deployment on failure

### 3. Code Quality
- [ ] Linting passes with zero warnings
- [ ] Type checking passes (if using typed language)
- [ ] No unused imports, variables, or dead code
- [ ] Consistent naming conventions throughout
- [ ] Functions focused and reasonably sized
- [ ] No duplicated logic where a shared utility is warranted
- [ ] File organization matches PLAN.md structure

### 4. Performance
- [ ] Database queries use indexes (no full table scans on large tables)
- [ ] No N+1 query patterns
- [ ] API responses within budget defined in PLAN.md
- [ ] Frontend bundle within size budget (if applicable)
- [ ] Images and assets optimized
- [ ] Caching implemented where specified in PLAN.md

### 5. Deployment Readiness
- [ ] All configuration via environment variables (no hardcoded values)
- [ ] `.env.example` documents all required variables
- [ ] Logging implemented for key operations
- [ ] Error handling returns meaningful messages
- [ ] Health check endpoint (if applicable)
- [ ] Database migrations tested and reversible
- [ ] Build process documented and reproducible

### 6. Live Verification (Browser-Based)
**CRITICAL**: This pillar requires using browser automation tools (Playwright or Chrome MCP)
to verify the application works from a real user's perspective. Do NOT skip this.
Do NOT ask the user to do this for you. YOU open the browser and check.

- [ ] Application starts and loads without errors
- [ ] Each user journey from SPEC.md works end-to-end in the browser:
  - [ ] Navigate to the feature
  - [ ] Interact with UI elements (click buttons, fill forms, submit)
  - [ ] Verify expected outcomes are visible on screen
  - [ ] Check at least one edge case (empty state, invalid input)
  - [ ] Verify error states display correctly
- [ ] No console errors in browser DevTools
- [ ] Pages load within performance budget
- [ ] Responsive layout works (if applicable — resize browser and check)
- [ ] Authentication flows work end-to-end (login, protected routes, logout)
- [ ] Data persists correctly (create something, refresh page, verify it's still there)

**How to execute this pillar**:
```
1. Start the dev server (npm run dev / equivalent)
2. Open browser via Playwright or Chrome MCP
3. Navigate to localhost:{port}
4. FOR each user journey in SPEC.md:
   - Follow the happy path step by step
   - Verify each step visually
   - Check the database state matches expectations
5. Capture evidence (screenshots, console output)
6. IF anything fails: fix it before marking this pillar complete
```

---

## Spec Cross-Check Protocol

After implementation, run this verification:

```
READ specs/SPEC.md

## Capability Check
FOR each capability in SPEC.md:
  STATUS: Implemented / Partially Implemented / Missing
  IF partially or missing:
    LIST: What's missing
    ASSESS: Is it blocking or deferrable?

## Invariant Check
FOR each invariant (INV-{NNN}):
  ENFORCED: yes/no — where in code?
  TESTED: yes/no — which test?
  IF not enforced or not tested:
    FLAG as critical gap

## Journey Check
FOR each user journey:
  HAPPY PATH: Does it work end-to-end?
  EDGE CASES: Are they handled?
  ERROR STATES: Do they show appropriate messages?
```

```
READ specs/PLAN.md

## Touchpoint Check
FOR each touchpoint:
  EXISTS: Does the file exist?
  CONTENT: Does it contain what was specified?
  IF missing or wrong:
    FLAG with specific gap description

## Effect Check
FOR each effect:
  IMPLEMENTED: Is the side-effect produced?
  VERIFIED: Can it be tested/observed?
  IF not implemented:
    FLAG as implementation gap
```

---

## When to Run Validation

| Trigger | What to Run |
|---------|-------------|
| After each task | That task's validation criteria |
| After each layer completes | Relevant pillar checks for that layer |
| After all tasks complete | Full 5-pillar validation + spec cross-check |
| Before presenting to user | Complete checklist |
| After user-requested changes | Regression check on affected pillars |

---

## R-TAP (Recursive Think-Answer Process)

For complex implementation tasks, use this self-check pattern:

```
BEFORE generating code:
  1. Think: What are the requirements for this task?
  2. Plan: What's the approach?
  3. Confidence check: Am I confident this will work?
     IF confidence < HIGH:
       Re-think: What am I uncertain about?
       Research: Check docs, examples, existing code
       Re-plan: Adjust approach
       Re-check confidence
       REPEAT until confident or 3 iterations
  4. Generate code
  5. Self-review: Does this match the plan? Does it satisfy invariants?
```

This prevents "generate first, debug later" patterns that consume context window.
