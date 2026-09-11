# Trode

A macOS menu bar app that displays Claude Code usage stats and skill review scores from Tessl.

## Prerequisites

- **Node.js** 18+
- **macOS** (menu bar app)
- **Tessl CLI** (optional, for live score lookups)

## Installation

```bash
# Clone the repo
git clone https://github.com/fernandezbaptiste/trode
cd trode

# Install dependencies
cd app
npm install
```

## Running the App

### Development Mode

```bash
cd app
npm start
```

The app will appear in your macOS menu bar. Click the icon to open the popover.

### With a Specific Project

Point to a project directory to scan its `.claude/skills/` folder:

```bash
SKILLS_PROJECT_PATH=/path/to/your/project npm start
```

### Demo Mode

Run with the included demo project (4 sample skills):

```bash
SKILLS_PROJECT_PATH=../demo-project npm start
```

## Building for Distribution

```bash
cd app
npm run package
```

Creates `Trode-0.1.0-arm64.dmg` in `app/release/`.

## Project Structure

```
trode/
├── app/                          # Electron app
│   ├── src/
│   │   ├── main/                 # Main process
│   │   │   ├── index.ts          # IPC handlers
│   │   │   └── tray.ts           # Menu bar tray
│   │   ├── preload/              # Context bridge
│   │   ├── renderer/             # React UI
│   │   │   ├── components/
│   │   │   │   ├── UsagePanel.tsx
│   │   │   │   ├── SkillsPanel.tsx
│   │   │   │   └── Footer.tsx
│   │   │   └── styles.css
│   │   └── services/
│   │       ├── claudeUsage.ts    # Usage stats (mock)
│   │       ├── skillsScanner.ts  # Scans .claude/skills/
│   │       └── tesslService.ts   # Tessl review scores
│   └── package.json
├── demo-project/                 # Sample skills for testing
│   └── .claude/skills/
│       ├── frontend-design/
│       ├── karpathy-guidelines/
│       ├── remotion-best-practices/
│       └── vercel-react-best-practices/
└── scripts/
    └── download-demo-skills.sh   # Fetches real skills from GitHub
```

## How It Works

### Skills Scanning

The app scans two locations for skills:

1. **Project skills**: `$SKILLS_PROJECT_PATH/.claude/skills/*/SKILL.md`
2. **Global skills**: `~/.claude/skills/*/SKILL.md`

Each subdirectory with a `SKILL.md` file is detected as an installed skill.

### Review Scores

Skills are scored using Tessl's review evaluation system:

| Score | Color | Meaning |
|-------|-------|---------|
| ≥70%  | Green | High quality |
| 50-70% | Yellow | Moderate |
| <50%  | Red | Low quality |
| —     | Gray | No evaluation |

Score lookup order:
1. Tessl CLI (`tessl search`) if installed
2. Fallback to known scores in `tesslService.ts`

### Usage Stats

Currently displays mock data. The structure supports parsing `~/.claude/projects/` for real usage stats (see `claudeUsage.ts`).

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SKILLS_PROJECT_PATH` | Project directory to scan for skills | None (global only) |

### Window Settings

Edit `app/src/main/tray.ts`:

```typescript
const WINDOW_WIDTH = 360;
const WINDOW_HEIGHT = 520;
```

## Tessl CLI Integration

For live score lookups, install the Tessl CLI:

```bash
npm install -g @tessl/cli
tessl login
```

The app will automatically use the CLI when available.

## Development

### Tech Stack

- **Electron** - Desktop app framework
- **React** - UI components
- **TypeScript** - Type safety
- **Vite** - Build tooling

### Adding New Skills to Fallback Scores

Edit `app/src/services/tesslService.ts`:

```typescript
const KNOWN_REVIEW_SCORES: Record<string, number> = {
  'frontend-design': 64,
  'karpathy-guidelines': 86,
  // Add more here
};
```

### Customizing the UI

- Styles: `app/src/renderer/styles.css`
- Colors defined as CSS variables in `:root`
- Typography: JetBrains Mono + IBM Plex Sans

## Troubleshooting

**App doesn't appear in menu bar**
- Check that no other Electron instance is running: `pkill -f Electron`

**Skills not showing**
- Verify skills exist at the scanned paths
- Each skill needs a `SKILL.md` file in its directory

**Review scores showing "—"**
- The skill isn't in the fallback list
- Tessl CLI not installed or skill not in registry

## License

MIT
