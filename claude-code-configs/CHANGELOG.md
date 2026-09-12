# Changelog

All notable changes to the Claude Code Configs project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-beta.1] - 2025-08-20

### 🚀 Beta Release - Ready for NPM

#### Major Changes
- **NPM Package Ready** - Complete package structure with all required files
- **Production-Ready CLI** - Stable command-line interface with comprehensive features
- **43 Passing Tests** - Full test coverage for core functionality
- **Zero Vulnerabilities** - Security audit passed with no issues

#### Package Updates
- **Added LICENSE file** to package directory for proper npm distribution
- **Added CHANGELOG.md** to package for version history
- **Verified all package.json files** paths exist and are correct
- **Tested npm pack** and local installation successfully

#### Features Included
- Intelligent configuration merging without duplication
- Interactive and batch mode support
- Automatic backup of existing configurations
- Git integration with .gitignore updates
- Validation and dry-run commands
- Support for all 7 configuration packages

#### Configurations Available
- **Frameworks:** Next.js 15
- **UI/Styling:** shadcn/ui, Tailwind CSS
- **Databases:** Drizzle ORM
- **Tooling:** Vercel AI SDK
- **MCP Servers:** Memory MCP Server, Token-Gated MCP Server

#### Known Limitations (Beta)
- NPM publication pending (use local installation)
- Some optional visual dependencies may not display
- Minor edge cases in complex multi-config scenarios

#### Installation
```bash
# Local installation (current method)
git clone https://github.com/Matt-Dionis/claude-code-configs.git
cd claude-code-configs/claude-config-composer
npm install && npm run build
node dist/cli.js [configs...]

# NPM installation (coming soon)
npx claude-config-composer [configs...]
```

## [0.9.1] - 2025-08-20

### 🐛 Critical Fixes

#### Fixed Directory Structure
- **CLAUDE.md now generates at root level** as expected (not in parent directory)
- **Proper .claude/ subdirectory structure** with settings.json, agents/, commands/, hooks/
- **Consistent output paths** for both interactive and batch modes

#### NPM Compatibility
- **Fixed configuration path resolution** for both local development and npm installation
- **Package now works correctly when installed globally** via npm

### ✨ New Features

#### CLI Commands
- **`validate [path]`** - Validate existing Claude Code configurations
- **`dry-run <configs...>`** - Preview what would be generated without creating files
- **Both commands provide detailed feedback** about configuration structure and compatibility

#### Progress Indicators
- **Step-by-step progress** during configuration generation
- **Clear status updates** for parsing, merging, and validation
- **File counts** displayed for agents, commands, and hooks

#### Structure Validation
- **Automatic validation** after generation ensures correct structure
- **Warnings displayed** for any missing or malformed files
- **Comprehensive checks** for all required components

### 🔧 Improvements

- **Better error messages** with helpful tips for common issues
- **Cleaner CLI output** with improved formatting
- **Fixed .gitignore handling** - only adds .claude/ when appropriate
- **Updated success messages** to accurately reflect generated structure

### 📦 Package Updates

- **Version bumped to 0.9.1** throughout codebase
- **Tested npm package installation** and global usage
- **All 89 tests passing** with comprehensive coverage

### 📝 Documentation

- **Updated README** with correct structure examples
- **Fixed path descriptions** in generated documentation
- **Clarified output directory behavior** in CLI help

## [0.9.0] - 2025-08-20

### 🚧 Beta Release - Complete Restructure

**IMPORTANT: This is a beta release (v0.9.0) preparing for the stable v1.0.0 release with NPM publishing.**

### 🔒 Security
- **Fixed critical vulnerability** in `minimist` dependency (CVE advisories GHSA-vh95-rmgr-6w4m, GHSA-xvch-5gv4-984h)
- Updated `asciify` to v1.3.2 to resolve transitive dependency issues
- All security vulnerabilities resolved (0 remaining)

### 🧹 Maintenance
- **Cleaned build artifacts** from dist directory (removed cli-old.js, cli-no-nav.js, etc.)
- **Added comprehensive migration guide** (MIGRATION.md) for users upgrading from v0.x
- **Updated version** to 0.9.0 for beta release period
- **Validated .npmignore** for proper NPM publishing preparation
- **89 tests passing** - comprehensive test coverage maintained

### 🎉 Major Architectural Changes

This release represents a complete overhaul of the claude-code-configs repository with significant breaking changes and new functionality.

### ✨ Added

#### **New CLI Tool: claude-config-composer**
- **Interactive CLI** for generating combined configurations
- **Intelligent config merging** without duplication
- **Conflict detection** for incompatible configurations
- **Automatic backups** of existing .claude directories
- **Git integration** with automatic .gitignore updates
- **Zero installation** with future NPX support
- **TypeScript-based** with comprehensive error handling

#### **New Configuration System**
- **Registry-based** configuration management
- **Priority-based** section merging
- **Dependency resolution** and validation
- **Framework-agnostic** configuration generation

#### **New Configurations**
- **Complete shadcn/ui configuration** (~4,000 lines)
  - 10 specialized agents for UI development
  - 8 powerful commands for component workflows
  - 4 automation hooks for validation and formatting
  - Comprehensive accessibility patterns
  - Performance optimization strategies

### 🏗️ Changed

#### **BREAKING CHANGES**
- **Repository structure completely reorganized**
  - Old: Configs at root level (`memory-mcp-server/`, `nextjs-15/`, etc.)
  - New: Configs in `configurations/` directory by category
- **Installation process changed**
  - Old: Direct copy from config directories  
  - New: Use CLI tool for intelligent merging
- **File paths updated** throughout documentation

#### **New Directory Structure**
```text
configurations/
├── frameworks/     # Next.js 15, React 19 (coming soon)
├── ui/            # shadcn/ui, Tailwind CSS
├── databases/     # Drizzle ORM, Prisma (coming soon) 
├── tooling/       # Vercel AI SDK, development tools
└── mcp-servers/   # Memory MCP, Token-gated MCP
```

### 📚 Documentation

- **Comprehensive README overhaul** with new usage patterns
- **CLI tool documentation** with examples and use cases  
- **Migration guide** for existing users
- **Professional package documentation** ready for NPM

### 🔧 Technical Improvements

- **TypeScript throughout** with strict type checking
- **Zod validation** for configuration schemas
- **Jest/Vitest testing** setup (tests in progress)
- **Professional build pipeline** with automated permissions
- **Dependency management** with optional packages for enhanced visuals

### 🚀 Future Ready

- **NPM publication ready** with proper package.json
- **Semantic versioning** implemented
- **Contribution guidelines** updated
- **Community-ready** with issue templates

---

## Migration Guide for Existing Users

If you were using the old structure:

### Before (v0.x)
```bash
# Old method
cp -r memory-mcp-server/.claude your-project/
cp memory-mcp-server/CLAUDE.md your-project/
```

### After (v0.9.0 Beta)
```bash  
# New method - much more powerful
git clone https://github.com/Matt-Dionis/claude-code-configs.git
cd claude-code-configs/claude-config-composer
npm install && npm run build

# From your project directory
node /path/to/claude-code-configs/claude-config-composer/dist/cli.js nextjs-15 shadcn
```

**Note:** NPM package with `npx` support coming in v1.0.0!

### Configuration Mapping

- `memory-mcp-server/` → `configurations/mcp-servers/memory-mcp-server/`
- `nextjs-15/` → `configurations/frameworks/nextjs-15/`
- `shadcn/` → `configurations/ui/shadcn/`
- `token-gated-mcp-server/` → `configurations/mcp-servers/token-gated-mcp-server/`

All configurations have been preserved and enhanced with additional content.

---

## What's Next

- **NPM Publication** - `npx claude-config-composer` coming soon
- **More Configurations** - React 19, Prisma, tRPC, Vitest
- **Web UI** - Browser-based configuration generator
- **VS Code Extension** - IDE integration
- **Community Registry** - User-contributed configurations

---

**⭐ If you find this project helpful, please star the repository!**