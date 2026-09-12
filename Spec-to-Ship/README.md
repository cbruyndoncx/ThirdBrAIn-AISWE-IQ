# Spec-to-Ship

A product development pipeline for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — from idea to PRD to spec to shipped product. These skills work together to front-load all thinking before writing code, enabling one-shot implementation of large features and small products.

## The Pipeline

```
Idea  ->  PRD  ->  Spec  ->  Plan  ->  Tasks  ->  Ship
         (prd-     (spec-driven-dev)
         builder)
```

**PRD Builder** captures what you're building and why — structured discovery, market research, and a comprehensive product requirements document.

**Spec-Driven Development** takes those requirements and turns them into technical specs (SPEC.md, PLAN.md, TASKS.md) that Claude can execute in one shot.

Together, they eliminate the back-and-forth that kills momentum when building with AI.

## Skills

| Skill | What It Does |
|-------|--------------|
| [prd-builder](./prd-builder/) | Structured discovery interviews, market research, and PRD generation for new or existing products |
| [spec-driven-dev](./spec-driven-dev/) | 4-phase protocol (Specify, Plan, Tasks, Implement) that produces LLM-optimized specs for one-shot builds |

## Installation

```bash
git clone https://github.com/mrtblount/Spec-to-Ship.git

# Copy both skills
cp -R Spec-to-Ship/prd-builder ~/.claude/skills/prd-builder
cp -R Spec-to-Ship/spec-driven-dev ~/.claude/skills/spec-driven-dev
```

## Usage

### Starting from scratch
Tell Claude what you want to build. PRD Builder activates for discovery, then Spec-Driven Dev takes over for technical planning and implementation.

### Adding a major feature
Describe the feature. Spec-Driven Dev detects the scope, specs it out, and builds it.

### Quick triggers
- "Build me an app that..."
- "Spec this out"
- "One-shot this"
- `/prd-builder` or `/spec-driven-dev`

## Related Repos

- [Specialized Skills](https://github.com/mrtblount/Specialized-Skills) — Individual Claude Code skills for various workflows and integrations
- [Skill Ecosystem](https://github.com/mrtblount/skill-ecosystem) — Framework, builder tools, and skill development infrastructure

## Links

- [tonyblount.com](https://tonyblount.com) — Portfolio
- [Four30.co](https://four30.co) — Consulting
- [LinkedIn](https://www.linkedin.com/in/williamblount/)

## License

MIT — see [LICENSE](./LICENSE)
