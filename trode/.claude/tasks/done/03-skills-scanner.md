# Task: Skills Scanner

## Goal

Scan and display installed skills from .claude/skills/ directories.

## Definition of Done

- [ ] skillsScanner.ts finds skills in ~/.claude/skills/
- [ ] skillsScanner.ts finds skills in $PROJECT/.claude/skills/
- [ ] SkillsPanel.tsx lists skill name + source (project/global)
- [ ] Shows "No skills found" if empty
- [ ] SKILLS_PROJECT_PATH env var overrides project path
- [ ] Skills show gray "no eval" badges (no scores yet)
- [ ] Extracts first line of SKILL.md as description

## Files to Create/Modify

```
app/src/services/
└── skillsScanner.ts

app/src/renderer/components/
└── SkillsPanel.tsx
```

## Environment Variable Support

```bash
# Use a specific project path for testing
SKILLS_PROJECT_PATH=./demo-project npm start
```

## UI Reference

```
┌─────────────────────────────────────┐
│  🧩 Skills Health    3 active       │
│  ❓ vercel-react-best...   no eval  │
│  ❓ frontend-design        no eval  │
│  ❓ my-custom-skill        no eval  │
└─────────────────────────────────────┘
```

## Constraints

- **DO NOT** implement Tessl eval scores yet (all gray badges)
- **DO NOT** implement the onboarding/setup panel yet
- **DO NOT** add colors yet (all skills are gray)

## Verification

```bash
# Create a test skill
mkdir -p ~/.claude/skills/test-skill
echo "# Test Skill" > ~/.claude/skills/test-skill/SKILL.md

cd app && npm start
# Should see "test-skill" in the skills list with gray badge
```
