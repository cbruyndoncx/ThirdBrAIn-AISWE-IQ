# Migration Guide: v0.x to v1.0

## 🚨 Breaking Changes

This repository has undergone a **complete architectural transformation** from individual configuration directories to a unified CLI tool that intelligently composes configurations.

## What's Changed

### Before (v0.x)
```
claude-code-configs/
├── nextjs-15/
│   └── .claude/
├── shadcn/
│   └── .claude/
└── [other configs]/
```
- Users manually copied entire `.claude/` directories
- No way to combine multiple configurations
- Configuration conflicts had to be resolved manually

### After (v1.0)
```
claude-code-configs/
├── claude-config-composer/     # New CLI tool
└── configurations/              # Organized configs
    ├── frameworks/
    ├── ui/
    ├── databases/
    └── tooling/
```
- Intelligent CLI merges multiple configurations
- Automatic conflict resolution
- Category-based organization

## Migration Steps

### For Existing Users

#### Option 1: Use the New CLI Tool (Recommended)

1. **Clone the updated repository:**
   ```bash
   git clone https://github.com/Matt-Dionis/claude-code-configs.git
   cd claude-code-configs/claude-config-composer
   ```

2. **Install and build the CLI:**
   ```bash
   npm install
   npm run build
   ```

3. **Generate your configuration:**
   ```bash
   # From your project directory
   node /path/to/claude-code-configs/claude-config-composer/dist/cli.js [configs...]
   
   # Example: Next.js + shadcn
   node /path/to/claude-config-composer/dist/cli.js nextjs-15 shadcn
   ```

#### Option 2: Access Individual Configs (Temporary)

Individual configurations have been moved to the `configurations/` directory:

- `nextjs-15` → `configurations/frameworks/nextjs-15/`
- `shadcn` → `configurations/ui/shadcn/`
- `prisma` → `configurations/databases/prisma/`
- etc.

**Note:** This option will be deprecated in future versions. We strongly recommend using the CLI tool.

### For Projects Using Git Submodules

If you were using this repository as a git submodule:

1. Update your submodule:
   ```bash
   git submodule update --remote
   ```

2. Update your scripts to use the new CLI:
   ```bash
   # Old way
   cp -r claude-code-configs/nextjs-15/.claude .
   
   # New way
   node claude-code-configs/claude-config-composer/dist/cli.js nextjs-15
   ```

### For CI/CD Pipelines

Update your automation scripts:

```bash
# Old approach
cp -r /configs/nextjs-15/.claude ./

# New approach
cd /your/project
node /configs/claude-config-composer/dist/cli.js nextjs-15 shadcn --no-interactive
```

## Configuration Mapping

| Old Location | New Location | CLI Name |
|--------------|--------------|----------|
| `/nextjs-15/` | `/configurations/frameworks/nextjs-15/` | `nextjs-15` |
| `/shadcn/` | `/configurations/ui/shadcn/` | `shadcn` |
| `/prisma/` | `/configurations/databases/prisma/` | `prisma` |
| `/drizzle/` | `/configurations/databases/drizzle/` | `drizzle` |
| `/tailwindcss/` | `/configurations/ui/tailwindcss/` | `tailwindcss` |
| `/vercel-ai-sdk/` | `/configurations/tooling/vercel-ai-sdk/` | `vercel-ai-sdk` |

## New Features You Get

### 1. **Intelligent Merging**
Combine multiple configurations without conflicts:
```bash
node cli.js nextjs-15 shadcn prisma typescript
```

### 2. **Interactive Selection**
Choose configurations through an intuitive UI:
```bash
node cli.js  # Opens interactive mode
```

### 3. **Automatic Backups**
Existing `.claude/` directories are automatically backed up before replacement.

### 4. **Git Integration**
`.claude/` is automatically added to `.gitignore`.

## Common Migration Scenarios

### Scenario 1: Next.js + shadcn Project
**Before:** Manually merged two directories, resolving conflicts by hand.

**After:**
```bash
node cli.js nextjs-15 shadcn
```

### Scenario 2: Full-Stack Application
**Before:** Copied 4-5 different configs, manually edited settings.json.

**After:**
```bash
node cli.js nextjs-15 shadcn prisma trpc typescript
```

### Scenario 3: Custom Configuration
**Before:** Modified configs directly in the repository.

**After:** Create a custom configuration in `configurations/` and register it in the CLI.

## Troubleshooting

### Q: Where did my favorite config go?
A: Check `configurations/[category]/[name]/`. The structure is preserved, just reorganized.

### Q: Can I still copy configs manually?
A: Yes, but it's not recommended. The CLI handles merging and conflicts better.

### Q: Will there be an npm package?
A: Yes! Coming soon: `npx claude-config-composer [configs]`

### Q: My CI/CD broke after updating
A: Update your scripts to use the new CLI path. See "For CI/CD Pipelines" above.

## Need Help?

- **Issues:** https://github.com/Matt-Dionis/claude-code-configs/issues
- **Documentation:** See the main README.md
- **Discord:** [Coming soon]

## Timeline

- **Now - v0.9.0:** Beta release with CLI tool
- **v1.0.0:** NPM package with `npx` support
- **v1.1.0:** Plugin system for custom configs
- **Future:** Deprecation of direct directory access

---

Thank you for your patience during this transition. The new architecture provides a much better experience for combining configurations and will enable exciting new features in the future.