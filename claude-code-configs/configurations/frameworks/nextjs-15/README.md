# Next.js 15 Claude Code Configuration 🚀

A comprehensive Claude Code configuration for building production-ready Next.js 15 applications with best practices, automated workflows, and intelligent assistance.

## ✨ Features

This configuration provides:

- **11 Specialized AI Agents** for different aspects of Next.js development
- **6 Powerful Commands** for common workflows
- **Intelligent Hooks** for automated validation and formatting
- **Optimized Settings** for Next.js development
- **Comprehensive Memory** with Next.js 15 best practices

## 📦 Installation

1. Copy the `.claude` directory to your Next.js project root:

```bash
cp -r nextjs-15/.claude your-nextjs-project/
cp nextjs-15/CLAUDE.md your-nextjs-project/
```

2. The configuration will be automatically loaded when you start Claude Code in your project.

## 🤖 Specialized Agents

### Core Development Agents

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `nextjs-app-router` | App Router routing expert | Creating pages, layouts, dynamic routes, parallel routes |
| `nextjs-server-components` | Server/Client component specialist | Optimizing component boundaries, fixing hydration issues |
| `nextjs-server-actions` | Server Actions expert | Forms, mutations, validation, progressive enhancement |
| `nextjs-data-fetching` | Data fetching & caching specialist | Fetch strategies, caching, revalidation, streaming |
| `nextjs-performance` | Performance optimization expert | Bundle analysis, Core Web Vitals, code splitting |

### Infrastructure & Testing Agents

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `nextjs-testing` | Testing framework specialist | Jest, Vitest, Playwright, Cypress setup |
| `nextjs-deployment` | Deployment & DevOps expert | Docker, Vercel, AWS, CI/CD pipelines |
| `nextjs-migration` | Migration specialist | Pages → App Router, version upgrades |
| `nextjs-security` | Security expert | Authentication, CSP, validation, OWASP |
| `nextjs-debugging` | Debugging specialist | React DevTools, error resolution, troubleshooting |
| `nextjs-typescript` | TypeScript expert | Type setup, fixing errors, type-safe patterns |

## 🛠️ Commands

### Quick Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/create-page` | Create a new page with proper structure | `/create-page products/[id]` |
| `/create-server-action` | Generate type-safe Server Action | `/create-server-action createUser user` |
| `/optimize-components` | Analyze and optimize component boundaries | `/optimize-components` |
| `/setup-testing` | Set up testing framework | `/setup-testing playwright` |
| `/analyze-performance` | Generate performance report | `/analyze-performance` |
| `/migrate-to-app-router` | Migrate from Pages Router | `/migrate-to-app-router /about` |

## 🪝 Intelligent Hooks

### Pre-commit Validation

- Validates Next.js 15 patterns (async params/searchParams)
- Checks for missing 'use client' directives
- Validates environment variable usage
- Runs TypeScript and ESLint checks

### Auto-formatting

- Formats TypeScript/JavaScript files with Prettier
- Validates Server Component patterns
- Suggests missing loading/error boundaries

### Smart Notifications

- Tips for better Next.js practices
- Warnings for common mistakes
- Performance suggestions

## ⚙️ Configuration

### Settings Overview

The configuration includes:

- **Permissions**: Safe defaults for Next.js development
- **Environment**: Optimized for Next.js workflows
- **Hooks**: Automated validation and formatting
- **Status Line**: Shows Next.js version and build status

### Customization

Edit `.claude/settings.json` to customize:

```json
{
  "permissions": {
    "allow": ["Write(app/**/*)", "Bash(npm run dev*)"],
    "deny": ["Read(.env.production)"]
  },
  "env": {
    "NEXT_PUBLIC_API_URL": "http://localhost:3000"
  }
}
```

## 🚀 Usage Examples

### Creating a New Feature

```bash
# 1. Create a new page with all necessary files
> /create-page dashboard/analytics

# 2. Claude will create:
# - app/dashboard/analytics/page.tsx
# - app/dashboard/analytics/loading.tsx
# - app/dashboard/analytics/error.tsx
```

### Optimizing Performance

```bash
# Analyze current performance
> /analyze-performance

# Claude will:
# - Run bundle analysis
# - Check Core Web Vitals
# - Identify optimization opportunities
# - Generate detailed report
```

### Setting Up Authentication

```bash
# Use the security agent
> Use the nextjs-security agent to set up authentication with NextAuth.js

# Claude will:
# - Configure NextAuth.js
# - Set up providers
# - Create middleware
# - Implement session management
```

## 📚 Best Practices Enforced

This configuration enforces Next.js 15 best practices:

1. **Server Components by Default** - Minimizes client-side JavaScript
2. **Proper Async Handling** - Handles async params/searchParams correctly
3. **Type Safety** - Full TypeScript support with proper types
4. **Security First** - Input validation, authentication, CSP
5. **Performance Optimized** - Code splitting, caching, streaming
6. **Testing Coverage** - Comprehensive testing setup
7. **Progressive Enhancement** - Forms work without JavaScript

## 🔄 Upgrading

To upgrade the configuration:

```bash
# Pull latest configuration
git pull origin main

# Copy updated files
cp -r nextjs-15/.claude your-project/
```

## 🤝 Contributing

Contributions are welcome! To improve this configuration:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

### Areas for Contribution

- Additional specialized agents
- More automation commands
- Enhanced hooks
- Testing improvements
- Documentation updates

## 📖 Documentation

Each component is fully documented:

- **Agents**: Detailed prompts and expertise areas
- **Commands**: Clear descriptions and examples
- **Hooks**: Validation logic and automation
- **Settings**: Permission patterns and configuration

## 🐛 Troubleshooting

### Common Issues

**Issue**: Hooks not executing

```bash
# Check hook permissions
chmod +x .claude/hooks/*.sh
```

**Issue**: Agent not responding

```bash
# Verify agent file exists
ls .claude/agents/
```

**Issue**: Commands not found

```bash
# Reload Claude Code configuration
# Exit and restart Claude Code
```

## 📝 License

MIT License - Feel free to use in your projects!

## 🙏 Acknowledgments

Built using:

- Official Next.js 15 documentation
- React 19 best practices
- Community feedback and patterns
- Production experience

---

**Made with ❤️ for the Next.js community**

*This configuration helps developers build better Next.js applications with Claude Code's intelligent assistance.*
