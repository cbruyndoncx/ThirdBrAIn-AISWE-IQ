## What Changed

<!-- Describe your changes in a few bullet points -->

-
-

## Which Component

<!-- Check all that apply -->

- [ ] Skill (`skills/ceos-*/`)
- [ ] Template (`templates/`)
- [ ] Setup script (`setup.sh`)
- [ ] Documentation (`docs/`, `README.md`, `CONTRIBUTING.md`)
- [ ] Data format (frontmatter fields, status enums, file naming)

## Before / After

<!-- For behavior changes: describe what happens before and after your change -->
<!-- For new features: describe what's now possible that wasn't before -->
<!-- For docs-only changes: you can skip this section -->

**Before:**

**After:**

## Testing

<!-- How did you verify this works? -->

- [ ] Ran `setup.sh` in a fresh directory
- [ ] Tested skill invocation in Claude Code
- [ ] Verified data files parse correctly
- [ ] Other (describe below)

## Security Review (for skill changes)

<!-- If your PR modifies any skill file (skills/ceos-*/SKILL.md), complete this checklist. -->
<!-- Skip this section for docs-only or template-only changes. -->

- [ ] Skill only accesses files within `data/` and `templates/`
- [ ] No external URLs, API calls, or network requests
- [ ] No credential handling (API keys, passwords, tokens)
- [ ] No shell command instructions (uses Claude's built-in file tools only)
- [ ] Shows content to user before writing any file (diff before write)

<!-- See CONTRIBUTING.md "Skill Security Review" for details on what reviewers look for. -->

## Breaking Changes

<!-- Does this change how existing users' data or workflows behave? -->

- [ ] **No breaking changes** — existing data and workflows are unaffected
- [ ] **Breaking change** — describe the migration path below:

---

*See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.*
*Changes to `templates/` and `docs/data-format-spec.md` require extra review — these are stability-critical files.*
