# Task: Tessl CLI Integration

## Goal

Integrate with Tessl CLI to show eval scores and handle onboarding.

## Definition of Done

- [ ] tesslCli.ts detects if tessl CLI is installed (`tessl --version`)
- [ ] tesslCli.ts detects if user is authenticated (`tessl whoami`)
- [ ] TesslSetup.tsx shows onboarding panel if CLI not configured
- [ ] TesslSetup.tsx has "Run tessl login" button that triggers login
- [ ] Skills are color-coded by lift value (green/yellow/red/gray)
- [ ] "Free evals on tessl.io →" link opens in browser
- [ ] Hardcoded eval scores work as fallback

## Files to Create/Modify

```
app/src/services/
└── tesslCli.ts

app/src/renderer/components/
├── TesslSetup.tsx      (new)
└── SkillsPanel.tsx     (update for colors)
```

## Color Coding Rules

| Icon | Condition | Color |
|------|-----------|-------|
| ✅ | lift >= +5 | Green |
| ⚠️ | lift 0 to +5 | Yellow |
| ❌ | lift < 0 | Red |
| ❓ | no eval data | Gray |

## Hardcoded Eval Scores

```typescript
const KNOWN_EVAL_SCORES = {
  'agent-browser': { score: 71, lift: 42.5 },
  'remotion-best-practices': { score: 100, lift: 25.5 },
  'remotion': { score: 100, lift: 25.5 },
  'frontend-design': { score: 90.3, lift: 24.6 },
  'vercel-react-best-practices': { score: 78.5, lift: 16.5 },
  'karpathy-guidelines': { score: 88.3, lift: -3.5 }, // NEGATIVE!
};
```

## TesslSetup Panel UI

```
┌─────────────────────────────────────┐
│  🔧 Setup Required                  │
│                                     │
│  To see skill eval scores, install  │
│  the Tessl CLI:                     │
│                                     │
│  npm install -g @tessl/cli          │
│                                     │
│  Then authenticate:                 │
│                                     │
│  [Run tessl login]  ← button        │
│                                     │
│  📖 View docs at docs.tessl.io      │
└─────────────────────────────────────┘
```

## Constraints

- Shell out to tessl CLI (don't use API directly)
- Use hardcoded scores as primary source (CLI may not return eval data)
- Don't block the app if tessl is missing - show setup panel instead

## Verification

```bash
# Test 1: Without tessl installed
cd app && npm start
# Should see TesslSetup onboarding panel

# Test 2: With tessl installed and logged in
npm install -g @tessl/cli
tessl login
cd app && npm start
# Should see skills with colored eval scores
```
