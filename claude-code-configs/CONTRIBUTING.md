# Contributing to Claude Code Configs

Thank you for your interest in contributing to Claude Code Configs! This project thrives on community contributions, and we welcome configs for new frameworks, improvements to existing configurations, and enhancements to the CLI tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Adding a New Configuration](#adding-a-new-configuration)
- [Improving Existing Configurations](#improving-existing-configurations)
- [Contributing to the CLI Tool](#contributing-to-the-cli-tool)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## How to Contribute

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/claude-code-configs.git
cd claude-code-configs
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

See specific sections below for different types of contributions.

### 4. Test Your Changes

```bash
cd claude-config-composer
npm install
npm test
npm run build
```

### 5. Submit a Pull Request

Push your branch and create a PR against the `main` branch.

## Adding a New Configuration

### Structure Requirements

Create your configuration in the appropriate category:

```
configurations/
├── frameworks/     # React, Vue, Angular, etc.
├── ui/            # Component libraries, CSS frameworks
├── databases/     # ORMs, database tools
├── tooling/       # Build tools, SDKs
└── mcp-servers/   # MCP server implementations
```

### Required Files

Each configuration must include:

```
your-config/
├── .claude/
│   ├── settings.json      # Permissions and environment variables
│   ├── agents/            # Specialized AI agents (optional)
│   ├── commands/          # Custom commands (optional)
│   └── hooks/            # Automation hooks (optional)
├── CLAUDE.md              # Main configuration and best practices
├── README.md              # Setup and usage instructions
└── package.json           # Metadata and version info
```

### package.json Format

```json
{
  "name": "@claude-code-configs/your-config",
  "version": "1.0.0",
  "description": "Brief description of your configuration",
  "keywords": ["claude-code", "your-framework"],
  "claude-config": {
    "category": "frameworks|ui|databases|tooling|mcp-servers",
    "priority": 10,
    "compatibility": {
      "requires": [],
      "conflicts": []
    }
  }
}
```

### CLAUDE.md Guidelines

Your CLAUDE.md should include:

1. **Project Context** - What this configuration is for
2. **Core Technologies** - List of main dependencies
3. **Security Best Practices** - Security considerations
4. **Development Patterns** - Framework-specific patterns
5. **Testing Approach** - How to test code
6. **Resources** - Links to documentation

### Quality Checklist

- [ ] Configuration works with Claude Code
- [ ] All file paths are correct
- [ ] Documentation is clear and complete
- [ ] No sensitive data (API keys, passwords)
- [ ] Tested with the CLI tool
- [ ] Added to registry if needed

## Improving Existing Configurations

### Types of Improvements

1. **Add New Agents** - Specialized expertise
2. **Create Commands** - Workflow automation
3. **Enhance Hooks** - Better automation
4. **Update Documentation** - Clarity and examples
5. **Fix Issues** - Bugs or errors

### Guidelines

- Maintain backward compatibility
- Test with existing projects
- Update version in package.json
- Document changes in PR

## Contributing to the CLI Tool

### Setup Development Environment

```bash
cd claude-config-composer
npm install
npm run dev -- nextjs-15 shadcn  # Test development mode
```

### Code Standards

- TypeScript with strict mode
- No `any` types without justification
- Comprehensive error handling
- Tests for new features
- JSDoc comments for public APIs

### Testing

```bash
# Run all tests
npm test

# Run specific test file
npm test -- config-parser.test.ts

# Run with coverage
npm run test:ci
```

### Common Tasks

#### Adding a New Command

1. Create command file in `src/cli/commands/`
2. Implement command class with `execute` method
3. Add to main CLI in `src/cli.ts`
4. Write tests in `tests/`

#### Modifying the Merger

1. Update logic in `src/merger/`
2. Ensure no duplicates are created
3. Test with multiple configurations
4. Verify priority ordering works

## Testing Guidelines

### Unit Tests

- Test individual functions
- Mock file system operations
- Cover edge cases
- Aim for >80% coverage

### Integration Tests

- Test full command execution
- Verify file generation
- Check configuration merging
- Test error scenarios

### Manual Testing

Before submitting PR:

```bash
# Test basic generation
node dist/cli.js nextjs-15 shadcn

# Test interactive mode
node dist/cli.js

# Test validation
node dist/cli.js validate

# Test dry-run
node dist/cli.js dry-run nextjs-15
```

## Pull Request Process

### PR Title Format

```
type(scope): brief description

Examples:
- feat(config): add Astro framework configuration
- fix(cli): resolve Windows path issues
- docs(readme): update installation instructions
- test(merger): add edge case tests
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New configuration
- [ ] Bug fix
- [ ] Feature enhancement
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process

1. Automated tests must pass
2. At least one maintainer review
3. Address feedback promptly
4. Squash commits before merge

## Questions?

Feel free to:
- Open an issue for discussion
- Ask in PR comments
- Check existing issues/PRs

Thank you for contributing! 🎉