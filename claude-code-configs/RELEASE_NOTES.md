# Release Notes - v0.9.0-beta

## 🚀 Major Architectural Transformation

We're excited to announce v0.9.0-beta, a complete reimagining of claude-code-configs that transforms it from a simple configuration collection into a powerful, intelligent CLI tool for generating custom Claude Code configurations.

### 🎯 What's New

#### **Introducing Claude Config Composer**
A brand new TypeScript CLI tool that intelligently merges multiple configurations for your exact tech stack.

```bash
# Generate a custom configuration combining multiple frameworks
node claude-config-composer/dist/cli.js nextjs-15 shadcn tailwindcss drizzle
```

**Key Features:**
- 🧠 **Intelligent Merging** - Combines multiple configs without duplication or conflicts
- 📦 **Zero Installation** (coming in v1.0.0) - Will support `npx` for instant use
- 🔄 **Automatic Backups** - Preserves existing `.claude/` directories
- 🔒 **Git Integration** - Auto-adds to `.gitignore`
- ✅ **89 Passing Tests** - Comprehensive test coverage
- 🎨 **Interactive Mode** - Visual selection of configurations

### 🚨 Breaking Changes

**IMPORTANT:** This release restructures the entire repository. If you're upgrading from a previous version, please read the [Migration Guide](MIGRATION.md).

#### Before (v0.x)
```bash
# Old method - manual copying
cp -r memory-mcp-server/.claude your-project/
```

#### After (v0.9.0)
```bash
# New method - intelligent composition
node claude-config-composer/dist/cli.js memory-mcp-server
```

**Configuration Location Changes:**
- `memory-mcp-server/` → `configurations/mcp-servers/memory-mcp-server/`
- `nextjs-15/` → `configurations/frameworks/nextjs-15/`
- `shadcn/` → `configurations/ui/shadcn/`
- See [Migration Guide](MIGRATION.md) for complete mapping

### ✨ New Configurations Added

#### **shadcn/ui Configuration** (4,000+ lines)
Complete configuration for building beautiful, accessible UIs with:
- 10 specialized UI development agents
- 8 powerful component workflow commands
- 4 automation hooks for validation
- Comprehensive accessibility patterns
- Performance optimization strategies

#### **Tailwind CSS Configuration**
Dedicated configuration for utility-first CSS development:
- Responsive design patterns
- Dark mode implementation
- Custom design systems
- Performance optimization

#### **Drizzle ORM Configuration**
Type-safe database operations with:
- Schema management patterns
- Migration workflows
- Type generation
- Query optimization

#### **Vercel AI SDK Configuration**
Build streaming AI applications with:
- Multi-provider support
- Function calling patterns
- Stream handling
- Error recovery strategies

### 📊 Repository Statistics

- **7 Complete Configurations** ready for use
- **40+ Specialized Agents** across all configs
- **25+ Custom Commands** for workflows
- **89 Tests** with full coverage
- **0 Security Vulnerabilities** (npm audit clean)

### 🔄 What's Coming in v1.0.0

The official v1.0.0 release will include:

1. **NPM Package Publication**
   ```bash
   npx claude-config-composer nextjs-15 shadcn
   ```

2. **Additional Configurations**
   - React 19 (standalone)
   - Prisma ORM
   - Vitest testing
   - tRPC
   - Zod validation

3. **Web UI** (planned)
   - Browser-based configuration builder
   - Visual dependency management

### 📦 Installation & Usage

#### Current Method (v0.9.0-beta)

```bash
# Clone and setup
git clone https://github.com/Matt-Dionis/claude-code-configs.git
cd claude-code-configs/claude-config-composer
npm install && npm run build

# Generate configuration from your project
cd /path/to/your/project
node /path/to/claude-config-composer/dist/cli.js nextjs-15 shadcn
```

#### Interactive Mode
```bash
# Launch interactive configuration selector
node /path/to/claude-config-composer/dist/cli.js
```

#### List Available Configurations
```bash
node /path/to/claude-config-composer/dist/cli.js list
```

### 🏗️ Popular Configuration Combinations

```bash
# Next.js + shadcn/ui
nextjs-15 shadcn

# Full-stack Next.js
nextjs-15 shadcn tailwindcss drizzle vercel-ai-sdk

# MCP Server Development
memory-mcp-server drizzle

# Token-gated Applications
token-gated-mcp-server vercel-ai-sdk
```

### 🔒 Security Updates

- Fixed critical vulnerability in `minimist` dependency
- Updated all dependencies to latest secure versions
- 0 vulnerabilities remaining (npm audit clean)

### 📚 Documentation Updates

- **[README.md](README.md)** - Complete overhaul with new usage patterns
- **[MIGRATION.md](MIGRATION.md)** - Comprehensive migration guide
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed change history
- Individual configuration READMEs updated

### 🤝 Contributing

We welcome contributions! The new architecture makes it easier than ever to add configurations:

1. Create a new directory in `configurations/[category]/[name]/`
2. Include `.claude/` directory with agents, commands, hooks
3. Add `CLAUDE.md` with best practices
4. Submit a PR

### 🙏 Acknowledgments

Thank you to the 400+ stargazers and contributors who have made this project possible. Your feedback and support drive these improvements.

### ⚠️ Beta Notice

This is a beta release (v0.9.0) preparing for the stable v1.0.0 release. While the code is production-ready, the NPM package has not yet been published. Use the local installation method described above.

### 🐛 Reporting Issues

Please report any issues on our [GitHub Issues](https://github.com/Matt-Dionis/claude-code-configs/issues) page.

### 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete list of changes.

---

**Ready to upgrade?** Check out the [Migration Guide](MIGRATION.md) for step-by-step instructions.

**New to claude-code-configs?** Jump straight to the [Quick Start](#installation--usage) section above.

Thank you for using claude-code-configs! 🚀