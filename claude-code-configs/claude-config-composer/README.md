# Claude Config Composer v1.0.0

Generate custom Claude Code configurations for your exact tech stack.

🎉 **Production Ready:** v1.0.0 - Full test coverage with 124 passing tests
📦 **NPM Package:** Available with `npm install -g claude-config-composer` or use `npx`

## 🚀 Quick Start

### NPX (Recommended - No Installation Required)

```bash
# In your project directory
npx claude-config-composer nextjs-15 shadcn
# Your .claude/ directory is created instantly
```

### Global Installation

```bash
# Install globally
npm install -g claude-config-composer

# Use anywhere
cd /path/to/your/project
claude-compose nextjs-15 shadcn
```

### Local Development

```bash
# Clone for development
git clone https://github.com/Matt-Dionis/claude-code-configs.git
cd claude-code-configs/claude-config-composer
npm install && npm run build

# Use from your project directory
cd /path/to/your/project
node /path/to/claude-code-configs/claude-config-composer/dist/cli.js nextjs-15 shadcn
```

## Common Stacks

```bash
# Next.js + shadcn/ui
npx claude-config-composer nextjs-15 shadcn

# Full-stack Next.js with database
npx claude-config-composer nextjs-15 shadcn drizzle tailwindcss

# Next.js with AI capabilities
npx claude-config-composer nextjs-15 vercel-ai-sdk

# Next.js with MCP server
npx claude-config-composer nextjs-15 memory-mcp-server
```

## Features

✅ **Zero installation** - Use npx without installing anything
✅ **Intelligent merging** - Combines configs without duplication
✅ **Automatic backups** - Preserves existing .claude/ configs
✅ **Git-friendly** - Auto-adds to .gitignore
✅ **Production ready** - 124 tests ensure reliability
✅ **TypeScript** - Full type safety throughout
✅ **Smart conflict resolution** - Handles overlapping configurations gracefully

## Advanced Usage

### Interactive Mode

```bash
# Opens interactive selection UI
npx claude-config-composer
```

### List Available Configs

```bash
npx claude-config-composer list
```

### Dry Run (Preview without creating files)

```bash
npx claude-config-composer nextjs-15 shadcn --dry-run
```

### Validate Configuration

```bash
npx claude-config-composer validate
```

### Skip Backup/Gitignore

```bash
npx claude-config-composer nextjs-15 shadcn --no-backup --no-gitignore
```

## What Gets Generated

```
your-project/
├── CLAUDE.md           # Combined documentation
└── .claude/
    ├── settings.json   # Merged settings
    ├── agents/         # Framework-specific agents
    ├── commands/       # Custom commands
    └── hooks/          # Development hooks
```

**Note:** No README.md or package.json files are generated - only Claude Code configuration files.

---

## 🛠️ Development & Contributing

### Local Development Setup

```bash
# Clone the config repository
git clone https://github.com/Matt-Dionis/claude-code-configs.git
cd claude-code-configs/claude-config-composer

# Install dependencies
npm install

# Build the CLI
npm run build

# Test locally
npm run dev nextjs-15 shadcn
```

## Available Configurations

### Frameworks

- **nextjs-15**: Next.js 15 with App Router, React 19, Server Components

### UI/Styling

- **shadcn**: shadcn/ui with Radix UI + Tailwind components
- **tailwindcss**: Tailwind CSS utility-first framework

### Tooling

- **vercel-ai-sdk**: Vercel AI SDK for building AI applications

### Databases

- **drizzle**: Drizzle ORM for TypeScript

### MCP Servers

- **memory-mcp-server**: Memory/knowledge management MCP server
- **token-gated-mcp-server**: Token-gated access MCP server
- **simple-mcp-server**: Basic MCP server template

## Test Coverage & CI

The project has comprehensive test coverage with 124 passing tests:

- ✅ **Unit Tests**: Core functionality testing
- ✅ **Integration Tests**: End-to-end CLI testing  
- ✅ **Config Validation**: All configurations verified
- ✅ **TypeScript**: Full type checking with no errors
- ✅ **CI/CD**: GitHub Actions on Node 18.x and 20.x

## How It Works

1. **Registry System**: Maintains metadata about each configuration including:
   - Dependencies and conflicts
   - Section priorities
   - Mergeable vs non-mergeable sections

2. **Smart Merging**: The merger:
   - Parses markdown structure
   - Identifies duplicate sections
   - Merges compatible content (e.g., commands)
   - Preserves framework-critical sections
   - Orders sections by priority

3. **Conflict Resolution**:
   - Detects incompatible configs
   - Suggests missing dependencies
   - Allows override with warnings

## Example Output

When you combine Next.js 15 + shadcn, the tool:

1. Preserves critical Next.js 15 breaking changes
2. Includes shadcn component patterns
3. Merges common commands from both
4. Combines security best practices
5. Maintains proper section hierarchy

## Architecture

```text
claude-config-composer/
├── src/
│   ├── cli.ts                      # CLI interface
│   ├── registry/
│   │   └── config-registry.ts      # Config metadata & validation
│   ├── parser/
│   │   └── config-parser.ts        # Parse existing configs
│   ├── merger/
│   │   ├── config-merger.ts        # Merge CLAUDE.md files
│   │   └── component-merger.ts     # Merge agents, commands, hooks
│   └── generator/
│       └── config-generator.ts     # Generate complete .claude structure
├── package.json
├── tsconfig.json
└── README.md
```

## Extending

To add a new configuration:

1. Create a config directory with `CLAUDE.md`
2. Add metadata to `config-registry.ts`:

```typescript
{
  id: 'your-config',
  name: 'Your Config',
  description: 'Description',
  version: '1.0.0',
  category: 'framework',
  dependencies: ['required-config'],
  conflicts: ['incompatible-config'],
  path: path.join(configsPath, 'your-config'),
  priority: 8,
  sections: [
    { title: 'Critical Section', mergeable: false, priority: 15 }
  ]
}
```

## Advanced Features

### Section Priorities

Sections are ordered by priority (higher first):

- Critical/Breaking changes: 15
- Core principles: 10
- Common commands: 5

### Mergeable Sections

These sections combine content from multiple configs:

- Common Commands
- Security Best Practices
- Testing Approaches
- Performance Optimization

### Non-Mergeable Sections

These sections are preserved from the highest priority config:

- Breaking Changes
- Critical Principles
- Framework-specific conventions

## Future Enhancements

- [ ] Web UI for config generation
- [ ] Config validation and linting
- [ ] Custom merge strategies
- [ ] Config inheritance chains
- [ ] Version compatibility matrix
- [ ] Export to different formats
- [ ] Config testing framework
- [ ] Community config registry

## Contributing

1. Fork the repository
2. Add your configuration
3. Update the registry
4. Test merging with existing configs
5. Submit a pull request

## License

MIT
