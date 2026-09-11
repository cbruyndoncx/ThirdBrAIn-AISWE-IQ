# Task: Demo Project + Polish

## Goal

Complete demo-project with real skills and write marketing-focused README.

## Definition of Done

- [ ] 4 real SKILL.md files downloaded to demo-project/
- [ ] README.md with Tessl signup flow written
- [ ] Screenshot of app added to README
- [ ] SKILLS_PROJECT_PATH=./demo-project works correctly
- [ ] electron-builder creates working .dmg
- [ ] All 4 demo skills show correct lift values

## Demo Skills to Download

| Skill | Source | Lift |
|-------|--------|------|
| vercel-react-best-practices | vercel-labs/agent-skills | +16.5 |
| remotion-best-practices | remotion-dev/skills | +25.5 |
| frontend-design | anthropics/skills | +24.6 |
| karpathy-guidelines | forrestchang/andrej-karpathy-skills | **-3.5** ⚠️ |

## Download Script

Create `scripts/download-demo-skills.sh`:

```bash
#!/bin/bash
mkdir -p demo-project/.claude/skills/{vercel-react-best-practices,remotion-best-practices,frontend-design,karpathy-guidelines}

curl -o demo-project/.claude/skills/vercel-react-best-practices/SKILL.md \
  https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/vercel-react-best-practices/SKILL.md

curl -o demo-project/.claude/skills/remotion-best-practices/SKILL.md \
  https://raw.githubusercontent.com/remotion-dev/skills/main/skills/remotion/SKILL.md

curl -o demo-project/.claude/skills/frontend-design/SKILL.md \
  https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md

curl -o demo-project/.claude/skills/karpathy-guidelines/SKILL.md \
  https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/skills/karpathy-guidelines/SKILL.md
```

## README Structure

```markdown
# Trode

Track your Claude Code usage and find out which skills are helping (or hurting).

## The Problem

You've installed skills but have no idea if they help or hurt Claude's performance.
Tessl evaluates skills - some improve results by +25%, others actually make Claude worse!

## Quick Start

1. Install the Tessl CLI:
   npm install -g @tessl/cli

2. Create a free account:
   tessl login

3. Clone and run:
   git clone https://github.com/yourname/trode
   cd trode/app && npm install && npm start

## Try the Demo

SKILLS_PROJECT_PATH=./demo-project npm start

This shows 4 real skills including **karpathy-guidelines** which has -3.5 lift!

## Features

- 📊 Claude usage tracking (5-hour window, weekly, today)
- 🧩 Skills health check with Tessl evaluation scores
- 🎨 Color-coded effectiveness (green = good, red = bad)
- 🔗 Link to free skill evaluations on tessl.io

## Screenshot

[screenshot.png]
```

## Constraints

- Fetch real skills from official GitHub repos
- Keep README marketing-focused (not technical docs)
- Include "Free evals on tessl.io" call-to-action
- Screenshot should show demo skills with varied colors

## Verification

```bash
# Download skills
chmod +x scripts/download-demo-skills.sh
./scripts/download-demo-skills.sh

# Run with demo
SKILLS_PROJECT_PATH=./demo-project npm start
# Should see 4 skills:
# ✅ remotion-best-practices +25.5
# ✅ frontend-design +24.6
# ✅ vercel-react-best-practices +16.5
# ❌ karpathy-guidelines -3.5

# Build DMG
cd app && npm run package
# Should create .dmg in dist/
```
