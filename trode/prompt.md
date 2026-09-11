# Trode - Build Specification

A macOS menu bar app that tracks Claude Code usage AND shows skill evaluation scores from Tessl.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [User Journey & Marketing Funnel](#user-journey--marketing-funnel)
3. [Technical Architecture](#technical-architecture)
4. [UI Design](#ui-design)
5. [Implementation Details](#implementation-details)
6. [Demo Project Setup](#demo-project-setup)
7. [Task-Based Build Workflow](#task-based-build-workflow)
8. [Success Criteria](#success-criteria)

---

## Project Overview

### Goal

Build a menu bar app for macOS that:
1. Displays Claude Code usage stats (5-hour window, weekly limit, today's tokens/cost)
2. Scans installed skills from `.claude/skills/*/SKILL.md`
3. Fetches skill evaluation scores via Tessl CLI integration
4. **Provides a funnel to get users to sign up for Tessl** (key content marketing goal)

### Marketing Angle

> "Some of your skills might be making your agent worse"

The karpathy-guidelines skill has a **-3.5 lift** - meaning it actually makes Claude Code perform worse. This is the hook for the content marketing.

### Tech Stack

- **Runtime**: Electron (macOS menu bar app)
- **Frontend**: React + TypeScript
- **Build**: Vite + electron-builder
- **CLI Integration**: Shell out to `tessl` CLI
- **Data**: Parse `~/.claude/` for usage stats

---

## User Journey & Marketing Funnel

```
User sees Trode on social media / blog
         ↓
Clone the repo
         ↓
npm install -g @tessl/cli  ← TESSL INSTALL
         ↓
tessl login               ← TESSL SIGNUP (free account)
         ↓
npm install && npm start
         ↓
App shows skills with eval scores
         ↓
User sees "karpathy-guidelines: -3.5" 😱
         ↓
Clicks "Free evals on tessl.io →"  ← DEEPER ENGAGEMENT
```

This is a **content marketing project** - the app works well AND naturally encourages Tessl adoption through the required setup flow.

---

## Technical Architecture

### Project Structure

```
trode/
├── CLAUDE.md                    # Project state for Claude Code
├── prompt.md                    # This file (full specification)
├── .claude/
│   └── tasks/
│       ├── backlog/             # Planned tasks
│       ├── current/             # ONE active task
│       │   └── task.md
│       └── done/                # Completed tasks
├── app/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── electron-builder.json
│   └── src/
│       ├── main/
│       │   ├── index.ts         # Electron main process
│       │   └── tray.ts          # Menu bar tray management
│       ├── preload/
│       │   └── index.ts         # IPC bridge
│       └── renderer/
│           ├── index.html
│           ├── index.tsx
│           ├── App.tsx
│           ├── styles.css
│           └── components/
│               ├── UsagePanel.tsx
│               ├── SkillsPanel.tsx
│               ├── TesslSetup.tsx
│               ├── ProgressBar.tsx
│               └── Footer.tsx
├── app/src/services/
│   ├── claudeUsage.ts           # Parse ~/.claude/ for stats
│   ├── skillsScanner.ts         # Find .claude/skills/*/SKILL.md
│   └── tesslCli.ts              # Shell to tessl CLI
└── demo-project/
    └── .claude/
        └── skills/
            ├── vercel-react-best-practices/SKILL.md
            ├── remotion-best-practices/SKILL.md
            ├── frontend-design/SKILL.md
            └── karpathy-guidelines/SKILL.md
```

### Tessl CLI Integration

**Available Commands** (from https://docs.tessl.io/reference/cli-commands):

| Command | Purpose |
|---------|---------|
| `tessl login` | Authenticate via browser (WorkOS device flow) |
| `tessl whoami` | Show current user |
| `tessl search <query>` | Search registry |
| `tessl list --json` | List installed tiles |

**Implementation Strategy**:

1. Check `tessl --version` → Is CLI installed?
2. Check `tessl whoami` → Is user authenticated?
3. Use `tessl search` → Lookup skill in registry
4. Fallback → Use hardcoded eval scores from Tessl research

### Hardcoded Eval Scores

From Tessl's internal research (use these as fallback when CLI doesn't return eval data):

| Skill | Score | Lift | Note |
|-------|-------|------|------|
| agent-browser | 71% | +42.5 | Best performer |
| remotion-best-practices | 100% | +25.5 | |
| frontend-design | 90.3% | +24.6 | Anthropic's own |
| vercel-react-best-practices | 78.5% | +16.5 | |
| **karpathy-guidelines** | 88.3% | **-3.5** | ⚠️ NEGATIVE - key for marketing! |

---

## UI Design

### Main Popover Layout

```
┌─────────────────────────────────────┐
│  Claude Usage               Pro     │
├─────────────────────────────────────┤
│  ⏱ 5-Hour Window           20%     │
│  ████░░░░░░░░░░░░░░░░░             │
│  Resets in 4h 54m                   │
├─────────────────────────────────────┤
│  📅 Weekly                  51%     │
│  ██████████░░░░░░░░░░░             │
│  Resets Mon 2:59 PM                 │
├─────────────────────────────────────┤
│  📊 Today                           │
│  Messages:                      6   │
│  Tokens:                    753.2K  │
│  Est. Cost:                 $2.47   │
├─────────────────────────────────────┤
│  🧩 Skills Health    5 active       │
│  ✅ remotion-best-practices +25     │
│  ✅ frontend-design         +24     │
│  ✅ vercel-react-best...    +16     │
│  ❌ karpathy-guidelines     -3      │
│  ❓ my-custom-skill     no eval     │
│      Free evals on tessl.io →       │
├─────────────────────────────────────┤
│  Updated 0 sec ago              ↻   │
│  Settings                    Quit   │
└─────────────────────────────────────┘
```

### Color Coding

| Icon | Lift Value | Color |
|------|------------|-------|
| ✅ | +5 or higher | Green |
| ⚠️ | 0 to +5 | Yellow |
| ❌ | Negative | Red |
| ❓ | No eval data | Gray |

### TesslSetup Panel (Onboarding)

Shown when Tessl CLI is not configured:

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

---

## Implementation Details

### tesslCli.ts

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface TesslStatus {
  installed: boolean;
  authenticated: boolean;
  username?: string;
}

export interface SkillEval {
  skillName: string;
  score?: number;
  lift?: number;
  hasEval: boolean;
  registryUrl?: string;
}

// Hardcoded scores from Tessl research (fallback)
const KNOWN_EVAL_SCORES: Record<string, { score: number; lift: number }> = {
  'agent-browser': { score: 71, lift: 42.5 },
  'remotion-best-practices': { score: 100, lift: 25.5 },
  'remotion': { score: 100, lift: 25.5 },
  'frontend-design': { score: 90.3, lift: 24.6 },
  'vercel-react-best-practices': { score: 78.5, lift: 16.5 },
  'karpathy-guidelines': { score: 88.3, lift: -3.5 }, // NEGATIVE!
};

export async function checkTesslStatus(): Promise<TesslStatus> {
  try {
    await execAsync('tessl --version');
  } catch {
    return { installed: false, authenticated: false };
  }

  try {
    const { stdout } = await execAsync('tessl whoami');
    const username = stdout.trim();
    return { installed: true, authenticated: true, username };
  } catch {
    return { installed: true, authenticated: false };
  }
}

export async function runTesslLogin(): Promise<boolean> {
  try {
    await execAsync('tessl login');
    return true;
  } catch {
    return false;
  }
}

export async function searchSkillInRegistry(skillName: string): Promise<SkillEval | null> {
  try {
    const { stdout } = await execAsync(`tessl search "${skillName}" --json`);
    // Parse JSON output - structure may vary
    const results = JSON.parse(stdout);
    // TODO: Extract eval data from results if available
    return null;
  } catch {
    return null;
  }
}

export function getKnownEvalScore(skillName: string): SkillEval {
  const known = KNOWN_EVAL_SCORES[skillName];
  if (known) {
    return {
      skillName,
      score: known.score,
      lift: known.lift,
      hasEval: true,
      registryUrl: `https://tessl.io/registry?q=${encodeURIComponent(skillName)}`,
    };
  }
  return {
    skillName,
    hasEval: false,
  };
}

export async function getSkillEval(skillName: string): Promise<SkillEval> {
  // Try CLI first
  const registryResult = await searchSkillInRegistry(skillName);
  if (registryResult?.hasEval) {
    return registryResult;
  }
  
  // Fallback to hardcoded scores
  return getKnownEvalScore(skillName);
}
```

### skillsScanner.ts

```typescript
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface InstalledSkill {
  name: string;
  path: string;
  description?: string;
  source: 'project' | 'global';
}

export function scanForSkills(projectPath?: string): InstalledSkill[] {
  const skills: InstalledSkill[] = [];

  // Scan project-level skills
  if (projectPath) {
    const projectSkillsDir = path.join(projectPath, '.claude', 'skills');
    skills.push(...scanSkillsDirectory(projectSkillsDir, 'project'));
  }

  // Scan global skills
  const globalSkillsDir = path.join(os.homedir(), '.claude', 'skills');
  skills.push(...scanSkillsDirectory(globalSkillsDir, 'global'));

  return skills;
}

function scanSkillsDirectory(
  skillsDir: string, 
  source: 'project' | 'global'
): InstalledSkill[] {
  const skills: InstalledSkill[] = [];

  if (!fs.existsSync(skillsDir)) {
    return skills;
  }

  const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
  
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const skillPath = path.join(skillsDir, entry.name);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    if (fs.existsSync(skillMdPath)) {
      const content = fs.readFileSync(skillMdPath, 'utf-8');
      const description = extractDescription(content);

      skills.push({
        name: entry.name,
        path: skillPath,
        description,
        source,
      });
    }
  }

  return skills;
}

function extractDescription(content: string): string | undefined {
  // Try to get first line after any YAML frontmatter
  const lines = content.split('\n');
  let inFrontmatter = false;
  
  for (const line of lines) {
    if (line.trim() === '---') {
      inFrontmatter = !inFrontmatter;
      continue;
    }
    if (!inFrontmatter && line.trim()) {
      // First non-empty line outside frontmatter
      return line.replace(/^#\s*/, '').trim().slice(0, 100);
    }
  }
  return undefined;
}
```

### claudeUsage.ts

```typescript
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface UsageStats {
  fiveHourWindow: { percentage: number; resetsIn: string };
  weekly: { percentage: number; resetsAt: string };
  today: { messages: number; tokens: number; estimatedCost: number };
}

// Pricing (Claude Sonnet)
const PRICE_PER_1M_INPUT = 3;   // $3 per 1M input tokens
const PRICE_PER_1M_OUTPUT = 15; // $15 per 1M output tokens

export function getUsageStats(): UsageStats {
  // TODO: Implement real parsing of ~/.claude/projects/
  // For now, return mock data
  return getMockUsageStats();
}

export function getMockUsageStats(): UsageStats {
  return {
    fiveHourWindow: { percentage: 20, resetsIn: '4h 54m' },
    weekly: { percentage: 51, resetsAt: 'Mon 2:59 PM' },
    today: { messages: 6, tokens: 753200, estimatedCost: 2.47 },
  };
}

// Reference: https://github.com/Iamshankhadeep/ccseva
// for parsing ~/.claude/projects/ JSONL files
export function parseClaudeUsage(): UsageStats {
  const claudeDir = path.join(os.homedir(), '.claude', 'projects');
  
  if (!fs.existsSync(claudeDir)) {
    return getMockUsageStats();
  }

  // TODO: Parse JSONL conversation logs
  // Calculate tokens from conversation files
  // Estimate costs based on input/output token counts
  
  return getMockUsageStats();
}

export function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(1)}M`;
  }
  if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}K`;
  }
  return tokens.toString();
}

export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}
```

### package.json

```json
{
  "name": "trode",
  "version": "0.1.0",
  "description": "Claude Code usage monitor with Tessl skill evaluations",
  "main": "dist/main/index.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "start": "electron .",
    "package": "electron-builder"
  },
  "dependencies": {
    "electron-store": "^8.1.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "electron": "^28.0.0",
    "electron-builder": "^24.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vite-plugin-electron": "^0.28.0"
  },
  "build": {
    "appId": "io.tessl.trode",
    "productName": "Trode",
    "mac": {
      "target": "dmg",
      "category": "public.app-category.developer-tools"
    },
    "extraMetadata": {
      "LSUIElement": true
    }
  }
}
```

---

## Demo Project Setup

### Download Real Skills

Create `demo-project/.claude/skills/` with these real skills:

| Skill | Source URL | Lift |
|-------|------------|------|
| vercel-react-best-practices | https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/vercel-react-best-practices/SKILL.md | +16.5 |
| remotion-best-practices | https://raw.githubusercontent.com/remotion-dev/skills/main/skills/remotion/SKILL.md | +25.5 |
| frontend-design | https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md | +24.6 |
| karpathy-guidelines | https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/skills/karpathy-guidelines/SKILL.md | **-3.5** ⚠️ |

### Setup Script

```bash
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

### Running with Demo Project

```bash
SKILLS_PROJECT_PATH=./demo-project npm start
```

---

## Task-Based Build Workflow

### How It Works

This project uses a task-based workflow for iterative development:

1. **One task at a time** - Only one task in `.claude/tasks/current/`
2. **Clear Definition of Done** - Each task has checkboxes to complete
3. **Constraints** - Prevent scope creep with explicit "DO NOT" rules
4. **Branch per milestone** - Not per commit, but per working feature

### CLAUDE.md (Project State File)

Claude Code reads this file automatically. It tracks current state and points to the active task.

```markdown
# Trode

## Current State
- [ ] Milestone 1: Scaffold
- [ ] Milestone 2: Usage Panel
- [ ] Milestone 3: Skills Scanner
- [ ] Milestone 4: Tessl Integration
- [ ] Milestone 5: Demo + Polish

## Current Task
Read `.claude/tasks/current/task.md` before doing any work.

## Commands
cd app && npm install
cd app && npm start
cd app && npm run build
```

### Starting a Task

```bash
# 1. Create branch
git checkout -b feat/scaffold

# 2. Move task to current
mv .claude/tasks/backlog/01-scaffold.md .claude/tasks/current/task.md

# 3. Tell Claude Code:
"Read .claude/tasks/current/task.md and implement it."
```

### Completing a Task

```bash
# 1. Verify all DoD items
npm start  # Does it work?

# 2. Commit and push
git add -A && git commit -m "feat: scaffold electron app"
git push origin feat/scaffold

# 3. Merge to main

# 4. Move task to done
mv .claude/tasks/current/task.md .claude/tasks/done/01-scaffold.md
```

---

## Task Backlog

### Task 01: Scaffold Electron App

**File**: `.claude/tasks/backlog/01-scaffold.md`

```markdown
# Task: Scaffold Electron Menu Bar App

## Goal
Create a minimal Electron menu bar app with a React popover that shows placeholder text.

## Definition of Done
- [ ] Running `npm start` from `app/` directory launches the app
- [ ] Menu bar shows a tray icon (can use placeholder icon)
- [ ] Clicking tray icon opens a 320px wide popover window
- [ ] Popover has dark theme background (#1a1a1a)
- [ ] Popover shows "Trode" title text
- [ ] No dock icon appears (LSUIElement configured)
- [ ] "Quit" button closes the app cleanly
- [ ] No TypeScript or build errors

## Files to Create
app/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── electron-builder.json
├── src/
│   ├── main/
│   │   ├── index.ts
│   │   └── tray.ts
│   ├── preload/
│   │   └── index.ts
│   └── renderer/
│       ├── index.html
│       ├── index.tsx
│       ├── App.tsx
│       └── styles.css

## Technical Notes
- Use vite-plugin-electron for Electron + Vite integration
- Reference https://github.com/Iamshankhadeep/ccseva for tray patterns
- Popover should appear below/near the tray icon
- Use BrowserWindow with frame: false

## Constraints
- DO NOT implement usage tracking yet
- DO NOT implement skills scanning yet
- DO NOT implement Tessl integration yet
- Just get a working shell that opens and closes

## Verification
cd app && npm install && npm start
# Should see tray icon, click opens dark popover, quit works
```

---

### Task 02: Usage Panel UI

**File**: `.claude/tasks/backlog/02-usage-panel.md`

```markdown
# Task: Claude Usage Panel UI

## Goal
Implement the Claude usage display section with mock data.

## Definition of Done
- [ ] UsagePanel component shows 5-hour window with progress bar
- [ ] UsagePanel component shows weekly limit with progress bar
- [ ] "Today" section shows messages, tokens, and estimated cost
- [ ] Progress bars have gradient fills
- [ ] Numbers use monospace font
- [ ] Footer shows "Updated 0 sec ago" with refresh button (↻)
- [ ] UI matches the mockup in prompt.md
- [ ] All data comes from mock values in claudeUsage.ts

## Files to Create/Modify
app/src/renderer/components/
├── UsagePanel.tsx
├── ProgressBar.tsx
└── Footer.tsx
app/src/services/
└── claudeUsage.ts  (mock data)

## Mock Data
{
  fiveHourWindow: { percentage: 20, resetsIn: '4h 54m' },
  weekly: { percentage: 51, resetsAt: 'Mon 2:59 PM' },
  today: { messages: 6, tokens: 753200, estimatedCost: 2.47 }
}

## Constraints
- DO NOT implement real ~/.claude/ parsing yet
- DO NOT implement skills section yet
- DO NOT implement Tessl integration yet
- Settings button can be a placeholder

## Verification
cd app && npm start
# Popover shows usage stats with progress bars
```

---

### Task 03: Skills Scanner

**File**: `.claude/tasks/backlog/03-skills-scanner.md`

```markdown
# Task: Skills Scanner

## Goal
Scan and display installed skills from .claude/skills/ directories.

## Definition of Done
- [ ] skillsScanner.ts finds skills in ~/.claude/skills/
- [ ] skillsScanner.ts finds skills in $PROJECT/.claude/skills/
- [ ] SkillsPanel.tsx lists skill name + path
- [ ] Shows "No skills found" if empty
- [ ] SKILLS_PROJECT_PATH env var overrides project path
- [ ] Skills show gray "no eval" badges (no scores yet)

## Files to Create/Modify
app/src/services/
└── skillsScanner.ts
app/src/renderer/components/
└── SkillsPanel.tsx

## Environment Variable
SKILLS_PROJECT_PATH=./demo-project npm start

## Constraints
- DO NOT implement Tessl eval scores yet (all gray badges)
- DO NOT implement the onboarding panel yet

## Verification
# Create test skill
mkdir -p ~/.claude/skills/test-skill
echo "# Test Skill" > ~/.claude/skills/test-skill/SKILL.md

cd app && npm start
# Should see "test-skill" in the skills list
```

---

### Task 04: Tessl CLI Integration

**File**: `.claude/tasks/backlog/04-tessl-integration.md`

```markdown
# Task: Tessl CLI Integration

## Goal
Integrate with Tessl CLI to show eval scores and onboarding.

## Definition of Done
- [ ] tesslCli.ts detects if tessl CLI is installed
- [ ] tesslCli.ts detects if user is authenticated (tessl whoami)
- [ ] TesslSetup.tsx shows onboarding if not configured
- [ ] TesslSetup.tsx has "Run tessl login" button
- [ ] Skills are color-coded by lift value (green/yellow/red/gray)
- [ ] "Free evals on tessl.io →" link works
- [ ] Hardcoded scores work as fallback

## Files to Create/Modify
app/src/services/
└── tesslCli.ts
app/src/renderer/components/
├── TesslSetup.tsx
└── SkillsPanel.tsx (update for colors)

## Color Coding
- Green (✅): lift >= +5
- Yellow (⚠️): lift 0 to +5
- Red (❌): lift < 0
- Gray (❓): no eval data

## Constraints
- Shell out to tessl CLI (don't use API directly)
- Use hardcoded scores as primary source for now

## Verification
# Without tessl installed
cd app && npm start
# Should see TesslSetup onboarding panel

# With tessl installed and logged in
npm install -g @tessl/cli
tessl login
cd app && npm start
# Should see skills with colored eval scores
```

---

### Task 05: Demo Project + Polish

**File**: `.claude/tasks/backlog/05-demo-polish.md`

```markdown
# Task: Demo Project + Polish

## Goal
Complete demo-project with real skills and write README.

## Definition of Done
- [ ] 4 real SKILL.md files downloaded to demo-project/
- [ ] README.md with Tessl signup flow
- [ ] Screenshot in README showing the app
- [ ] SKILLS_PROJECT_PATH=./demo-project works correctly
- [ ] electron-builder creates working .dmg
- [ ] All 4 demo skills show correct lift values

## Demo Skills to Download
1. vercel-react-best-practices (+16.5)
2. remotion-best-practices (+25.5)
3. frontend-design (+24.6)
4. karpathy-guidelines (-3.5) ← THE HOOK!

## README Structure
# Trode

## The Problem
You've installed skills but don't know if they help or hurt.
Some skills improve Claude by +25%, others make it worse!

## Quick Start
1. npm install -g @tessl/cli
2. tessl login
3. git clone ... && cd trode
4. cd app && npm install && npm start

## Try the Demo
SKILLS_PROJECT_PATH=./demo-project npm start
Shows 4 skills including one with -3.5 lift!

## Features
- Claude usage tracking
- Skills health check with Tessl evals
- Color-coded effectiveness

## Constraints
- Fetch real skills from official GitHub repos
- Keep README marketing-focused
- Include "Free evals on tessl.io" CTA

## Verification
# Download skills
./scripts/download-demo-skills.sh

# Run with demo
SKILLS_PROJECT_PATH=./demo-project npm start
# Should see 4 skills with varied colors

# Build DMG
npm run package
# Should create .dmg in dist/
```

---

## Success Criteria

The project is complete when:

- [ ] ✅ Launches in macOS menu bar (no dock icon)
- [ ] ✅ Shows Claude usage stats (mock data OK initially)
- [ ] ✅ Scans .claude/skills/ directories
- [ ] ✅ Shows Tessl eval scores with colors
- [ ] ✅ Onboarding prompts when Tessl not configured
- [ ] ✅ Demo has 4 real skills with varied scores
- [ ] ✅ README guides through Tessl signup flow
- [ ] ✅ electron-builder creates working .dmg

---

## Quick Reference

### Commands

```bash
# Development
cd app && npm install
cd app && npm start

# With demo project
SKILLS_PROJECT_PATH=./demo-project npm start

# Build DMG
cd app && npm run package
```

### Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project state for Claude Code |
| `prompt.md` | Full specification (this file) |
| `.claude/tasks/current/task.md` | Active task |
| `app/src/services/tesslCli.ts` | Tessl CLI integration |
| `app/src/services/skillsScanner.ts` | Find installed skills |
| `app/src/services/claudeUsage.ts` | Parse usage stats |

### Branding

- App name: **Trode** (not "Tessl Skills Monitor")
- Subtle Tessl presence: "Free evals on tessl.io →" link
- No Tessl logo in UI
- README naturally leads to Tessl signup

---

*Last updated: January 2026*
