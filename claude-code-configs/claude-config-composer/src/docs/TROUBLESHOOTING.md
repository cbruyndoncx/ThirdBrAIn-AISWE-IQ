# Troubleshooting Guide

This guide helps you resolve common issues when using Claude Config Composer.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Loading Problems](#configuration-loading-problems)
- [Generation Failures](#generation-failures)
- [Permission Issues](#permission-issues)
- [Validation Errors](#validation-errors)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)
- [Debug Information](#debug-information)

## Installation Issues

### NPM Installation Fails

**Problem**: `npm install claude-config-composer` fails

**Solutions**:
1. **Check Node.js version**:
   ```bash
   node --version  # Should be >= 16.0.0
   ```

2. **Clear npm cache**:
   ```bash
   npm cache clean --force
   ```

3. **Use alternative registry**:
   ```bash
   npm install claude-config-composer --registry https://registry.npmjs.org/
   ```

4. **Check network connectivity**:
   ```bash
   npm config get proxy
   npm config get https-proxy
   ```

### Global Installation Issues

**Problem**: `npx claude-config-composer` command not found

**Solutions**:
1. **Install globally**:
   ```bash
   npm install -g claude-config-composer
   ```

2. **Use full npx path**:
   ```bash
   npx claude-config-composer@latest
   ```

3. **Check PATH environment**:
   ```bash
   echo $PATH
   npm config get prefix
   ```

### Permission Errors During Install

**Problem**: `EACCES` errors during installation

**Solutions**:
1. **Use npm without sudo** (recommended):
   ```bash
   npm config set prefix ~/.npm-global
   export PATH=~/.npm-global/bin:$PATH
   ```

2. **Fix npm permissions**:
   ```bash
   sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}
   ```

## Configuration Loading Problems

### Configuration Not Found

**Error**: `Configuration 'nextjs-15' not found`

**Solutions**:
1. **List available configurations**:
   ```bash
   npx claude-config-composer list
   ```

2. **Check spelling and case**:
   - Use exact configuration names from the list
   - Configuration IDs are case-sensitive

3. **Update to latest version**:
   ```bash
   npm update claude-config-composer
   ```

### Invalid Configuration Structure

**Error**: `Configuration directory structure is invalid`

**Solutions**:
1. **Check directory structure**:
   ```
   configuration-name/
   ├── .claude/
   │   ├── settings.json
   │   ├── agents/
   │   ├── commands/
   │   └── hooks/
   ├── CLAUDE.md
   └── package.json
   ```

2. **Validate JSON files**:
   ```bash
   # Check if settings.json is valid
   node -e "console.log(JSON.parse(require('fs').readFileSync('.claude/settings.json', 'utf8')))"
   ```

3. **Check file permissions**:
   ```bash
   ls -la .claude/
   # All files should be readable
   ```

### Registry Loading Fails

**Error**: `Failed to load configuration registry`

**Solutions**:
1. **Check internet connection** (for online registry)
2. **Verify local paths** (for local configurations)
3. **Clear temporary files**:
   ```bash
   rm -rf ~/.cache/claude-config-composer/
   ```

## Generation Failures

### Target Directory Issues

**Error**: `Cannot write to target directory`

**Solutions**:
1. **Check directory permissions**:
   ```bash
   ls -ld ./target-directory
   # Should show write permissions (w)
   ```

2. **Create directory manually**:
   ```bash
   mkdir -p ./my-project
   chmod 755 ./my-project
   ```

3. **Use different output directory**:
   ```bash
   npx claude-config-composer nextjs-15 --output ./different-path
   ```

### File Conflicts

**Error**: `File already exists and would be overwritten`

**Solutions**:
1. **Use force flag** (if safe):
   ```bash
   npx claude-config-composer nextjs-15 --force
   ```

2. **Backup existing files**:
   ```bash
   cp -r .claude .claude.backup
   ```

3. **Use different output directory**:
   ```bash
   npx claude-config-composer nextjs-15 --output ./new-config
   ```

4. **Remove conflicting files**:
   ```bash
   rm -rf .claude
   ```

### Merge Conflicts

**Error**: `Configuration merge failed due to conflicts`

**Solutions**:
1. **Check compatibility**:
   ```bash
   npx claude-config-composer validate nextjs-15 shadcn
   ```

2. **Use dry run to preview**:
   ```bash
   npx claude-config-composer nextjs-15 shadcn --dry-run
   ```

3. **Generate configurations separately**:
   ```bash
   npx claude-config-composer nextjs-15 --output ./config1
   npx claude-config-composer shadcn --output ./config2
   # Manually merge what you need
   ```

## Permission Issues

### File System Permissions

**Error**: `EACCES: permission denied`

**Solutions**:
1. **Check current directory permissions**:
   ```bash
   ls -ld .
   pwd
   ```

2. **Change directory ownership**:
   ```bash
   sudo chown -R $(whoami) .
   ```

3. **Run with appropriate permissions**:
   ```bash
   # Only if absolutely necessary
   sudo npx claude-config-composer nextjs-15
   ```

4. **Use home directory**:
   ```bash
   cd ~
   npx claude-config-composer nextjs-15 --output ./my-project
   ```

### Read-Only File System

**Error**: `EROFS: read-only file system`

**Solutions**:
1. **Check mount options**:
   ```bash
   mount | grep $(pwd)
   ```

2. **Use different directory**:
   ```bash
   cd /tmp
   npx claude-config-composer nextjs-15
   ```

3. **Remount with write permissions** (if appropriate):
   ```bash
   sudo mount -o remount,rw /path/to/filesystem
   ```

## Validation Errors

### Schema Validation Failures

**Error**: `Configuration does not match expected schema`

**Solutions**:
1. **Check YAML syntax**:
   ```bash
   # For YAML files
   python -c "import yaml; yaml.safe_load(open('file.yaml'))"
   ```

2. **Validate JSON syntax**:
   ```bash
   # For JSON files
   jq empty file.json
   ```

3. **Check required fields**:
   - Ensure all required frontmatter fields are present
   - Check that values match expected types

4. **Use validation command**:
   ```bash
   npx claude-config-composer validate ./my-config
   ```

### Frontmatter Issues

**Error**: `Invalid frontmatter in agent/command file`

**Solutions**:
1. **Check YAML frontmatter format**:
   ```markdown
   ---
   name: agent-name
   description: Agent description
   tools: [tool1, tool2]
   ---
   
   Agent content here...
   ```

2. **Validate frontmatter separately**:
   ```bash
   # Extract and validate frontmatter
   sed -n '/^---$/,/^---$/p' agent.md | head -n -1 | tail -n +2 | python -c "import yaml, sys; yaml.safe_load(sys.stdin)"
   ```

3. **Common frontmatter issues**:
   - Missing closing `---`
   - Invalid YAML syntax (indentation, colons)
   - Required fields missing (name, description)

## Performance Issues

### Slow Configuration Loading

**Problem**: Configuration loading takes too long

**Solutions**:
1. **Check disk space**:
   ```bash
   df -h
   ```

2. **Monitor I/O**:
   ```bash
   iostat 1 5
   ```

3. **Use SSD storage** if possible

4. **Reduce configuration size**:
   - Remove unused agents/commands
   - Optimize large markdown files

### Memory Usage Issues

**Problem**: High memory usage during generation

**Solutions**:
1. **Check available memory**:
   ```bash
   free -h
   ```

2. **Process fewer configurations at once**:
   ```bash
   # Instead of:
   npx claude-config-composer config1 config2 config3 config4
   
   # Do:
   npx claude-config-composer config1 config2
   npx claude-config-composer config3 config4 --output ./temp
   # Then merge manually
   ```

3. **Close other applications**

4. **Use streaming mode** (if available):
   ```bash
   npx claude-config-composer nextjs-15 --stream
   ```

## Common Error Messages

### `Module not found`

**Error**: `Cannot find module 'claude-config-composer'`

**Solutions**:
1. Reinstall the package:
   ```bash
   npm uninstall claude-config-composer
   npm install claude-config-composer
   ```

2. Check installation location:
   ```bash
   npm list claude-config-composer
   ```

### `Command not found`

**Error**: `claude-config-composer: command not found`

**Solutions**:
1. Use npx:
   ```bash
   npx claude-config-composer --help
   ```

2. Install globally:
   ```bash
   npm install -g claude-config-composer
   ```

### `Invalid configuration ID`

**Error**: `Configuration ID contains invalid characters`

**Solutions**:
1. Use only alphanumeric characters and hyphens
2. Check the list of valid configurations:
   ```bash
   npx claude-config-composer list
   ```

### `Network error`

**Error**: `Failed to fetch configuration from registry`

**Solutions**:
1. Check internet connection
2. Try again later
3. Use offline mode:
   ```bash
   npx claude-config-composer nextjs-15 --offline
   ```

## Debug Information

### Enable Verbose Logging

```bash
# Enable detailed logging
npx claude-config-composer nextjs-15 --verbose

# Enable debug mode
DEBUG=claude-config-composer* npx claude-config-composer nextjs-15
```

### System Information

Collect system information for bug reports:

```bash
# System info
echo "OS: $(uname -a)"
echo "Node: $(node --version)"
echo "NPM: $(npm --version)"
echo "Package: $(npm list claude-config-composer)"

# Directory info
echo "PWD: $(pwd)"
echo "Permissions: $(ls -ld .)"

# Configuration info
npx claude-config-composer --version
npx claude-config-composer list
```

### Log Analysis

Check logs for common patterns:

1. **Permission errors**: Look for `EACCES`, `EPERM`
2. **Path issues**: Look for `ENOENT`, path traversal warnings
3. **Memory issues**: Look for `ENOMEM`, `Maximum call stack`
4. **Network issues**: Look for `ENOTFOUND`, `ECONNRESET`

### Common Fixes Summary

| Issue Type | Quick Fix | Command |
|------------|-----------|---------|
| Permissions | Fix ownership | `sudo chown -R $(whoami) .` |
| Not found | List available | `npx claude-config-composer list` |
| Conflicts | Use force | `--force` flag |
| Network | Try offline | `--offline` flag |
| Validation | Check syntax | `npx ... validate` |
| Memory | Reduce batch | Process fewer configs |

## Getting Help

If you can't resolve your issue:

1. **Check GitHub Issues**: [GitHub Issues](https://github.com/Matt-Dionis/claude-code-configs/issues)
2. **Search Documentation**: This troubleshooting guide and API docs
3. **Create Bug Report**: Include system info and verbose logs
4. **Community Support**: Join discussions for help

### Bug Report Template

```
**System Information:**
- OS: 
- Node.js: 
- NPM: 
- Package Version: 

**Command Executed:**
```
npx claude-config-composer ...
```

**Expected Behavior:**
[What you expected to happen]

**Actual Behavior:**
[What actually happened]

**Error Output:**
```
[Full error message with --verbose]
```

**Additional Context:**
[Any other relevant information]
```

---

For more help, see the [API documentation](./API.md) or [security guidelines](./SECURITY.md).