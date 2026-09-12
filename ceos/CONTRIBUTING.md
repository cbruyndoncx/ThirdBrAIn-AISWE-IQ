# Contributing to CEOS

Thank you for your interest in improving CEOS! This project serves two communities, and we welcome contributions from both.

## Two Types of Contributors

### EOS Practitioners

You know EOS inside and out. You run L10s, set Rocks, and live the process. You may not be a git expert, and that's fine.

**How you can help:**

- Suggest improvements to how skills implement EOS processes
- Report when a skill doesn't match how EOS actually works in practice
- Propose new EOS workflows or tool integrations
- Improve templates based on real-world usage
- Review documentation for EOS accuracy

### Developers

You know Claude Code and AI tooling. You may not know EOS terminology, and that's fine.

**How you can help:**

- Improve skill implementations (better prompts, smarter workflows)
- Fix bugs in setup.sh or skill logic
- Add new features to the data format
- Improve documentation for technical accuracy
- Build adapters for other AI agents

## Getting Started

1. **Fork** this repository
2. **Clone** your fork: `git clone https://github.com/YOUR-USERNAME/ceos.git`
3. **Create a branch**: `git checkout -b my-improvement`
4. **Make your changes**
5. **Push** and open a Pull Request

## Contribution Paths

### New EOS Workflows

Have an idea for a new skill or workflow?

1. Open an **Issue** first — describe the EOS process and how it should work
2. We'll discuss the design collaboratively
3. Once agreed, submit a PR with the implementation

### Skill Improvements

Want to make an existing skill better?

1. Fork the repo
2. Modify the skill in `skills/ceos-*/SKILL.md`
3. Submit a PR with **before/after** examples showing the improvement

### Template Improvements

Templates are the starting point for new companies.

- PRs to `templates/` are **additive only** — never remove or rename existing templates
- New templates are welcome
- Improvements to existing templates should maintain backward compatibility

### Data Format Extensions

The data format (YAML frontmatter keys, status values) is a contract that tools depend on.

- **Non-breaking additions** (new optional fields): Submit a PR with documentation
- **Breaking changes** (renaming fields, changing status values): Open an RFC-style Issue first. Breaking changes require a major version bump.

### Bug Fixes

Found a bug?

1. Fork the repo
2. Fix the issue
3. Submit a PR with reproduction steps

## Protected Files

Some files require extra care:

| File/Area | Rule |
|-----------|------|
| Data format spec (frontmatter keys, status values) | RFC + major version for breaking changes |
| Skill names and triggers | Issue discussion first |
| Skill files (`skills/ceos-*/SKILL.md`) | Security review required — see [Skill Security Review](#skill-security-review) |
| `setup.sh` interface | Backward-compatible changes only |
| Templates | Additive only — never remove or rename |

## Pull Request Process

1. **One concern per PR** — don't mix unrelated changes
2. **Describe the change** — what it does and why
3. **Test your changes** — run `./setup.sh` to verify skills still install correctly
4. **Update docs** if your change affects how things work

All PRs are reviewed by the maintainer before merging.

## Skill Security Review

CEOS skills are natural language instructions that Claude Code follows with the user's full permissions — file access, command execution, and more. A malicious or poorly written skill could read sensitive files, modify data outside its scope, or trick users into unsafe actions. **Every skill PR gets a security review.**

### Red Flags

When reviewing a skill PR, watch for these patterns:

| Red Flag | Why It's Dangerous | Example |
|----------|-------------------|---------|
| File access outside `data/` and `templates/` | Could read/modify system files, credentials, or other repos | `Read ~/.ssh/id_rsa` or `Read ~/.env` |
| Shell commands beyond basic git | Could execute arbitrary code on the user's machine | `Run curl ... \| bash` or `Execute pip install ...` |
| External URLs or API calls | Could exfiltrate data to remote servers | `Send this data to https://example.com/collect` |
| Requests for credentials or API keys | Could harvest secrets | `Ask the user for their OpenAI API key` |
| Instructions to disable safety checks | Undermines existing guardrails | `Skip the diff preview` or `Write without asking` |
| Overly broad file operations | Could corrupt data across skills | `Delete all files in data/` or `Modify every .md file` |

### Review Checklist for Skill PRs

Before approving a skill PR, verify:

- [ ] **Scope**: Skill only reads/writes files within `data/` and `templates/` (plus its own `SKILL.md`)
- [ ] **No external calls**: Skill doesn't reference external URLs, APIs, or services
- [ ] **No credential handling**: Skill doesn't ask for or store API keys, passwords, or tokens
- [ ] **No shell commands**: Skill doesn't instruct Claude to run shell commands (except basic file operations)
- [ ] **Diff before write**: Skill shows content to the user before writing any file
- [ ] **Guardrails section**: Skill includes a `## Guardrails` section with appropriate constraints
- [ ] **Cross-skill boundaries**: Skill mentions other skills but doesn't auto-invoke them

### Security Manifest (Optional)

Skill authors can add optional frontmatter fields to make security review easier:

```yaml
---
name: ceos-example
description: Use when [trigger]
file-access: [data/example/, templates/example.md]
tools-used: [Read, Write, Glob]
---
```

These fields are not enforced — they're a convenience for reviewers to quickly verify that the skill's actual behavior matches its declared scope.

## Versioning

CEOS follows [Semantic Versioning](https://semver.org/):

- **Major** (1.0 → 2.0): Data format breaking changes
- **Minor** (1.0 → 1.1): New skills, new features
- **Patch** (1.0.0 → 1.0.1): Bug fixes, documentation

## Code of Conduct

Be kind, be constructive, be helpful. We're building tools for teams that want to run better businesses. Let's model that behavior here.

## Questions?

Open an Issue. There are no dumb questions — especially about EOS terminology or Claude Code concepts. The whole point of this project is bridging those two worlds.
