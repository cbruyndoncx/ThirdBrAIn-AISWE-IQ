# Security Guidelines

This document outlines security best practices and guidelines for Claude Config Composer.

## Table of Contents

- [Input Validation](#input-validation)
- [File System Security](#file-system-security)
- [Configuration Security](#configuration-security)
- [Dependency Security](#dependency-security)
- [Runtime Security](#runtime-security)
- [Reporting Security Issues](#reporting-security-issues)

## Input Validation

### User Input Sanitization

All user inputs are automatically sanitized and validated using Zod schemas to prevent injection attacks and ensure data integrity.

#### String Validation

```typescript
// All strings are validated against these rules:
const SafeString = z
  .string()
  .min(1, 'String cannot be empty')
  .max(1000, 'String too long')
  .refine(
    str => !/[\0-\x08\x0B\x0C\x0E-\x1F\x7F]/.test(str),
    'String contains invalid control characters'
  );
```

**Protected Against:**
- Null byte injection (`\0`)
- Control character injection
- Excessively long strings (DoS protection)
- Empty/whitespace-only strings

#### Path Validation

```typescript
// File paths are strictly validated:
const FilePathString = z
  .string()
  .min(1, 'File path cannot be empty')
  .max(500, 'File path too long')
  .transform(str => PathValidator.validatePath(str));
```

**Protected Against:**
- Path traversal attacks (`../`, `..\\`)
- Absolute path injection
- Reserved file names
- Invalid characters for the target OS
- Symbolic link attacks

#### Configuration ID Validation

```typescript
// Configuration IDs are sanitized:
const ConfigIdString = z
  .string()
  .min(1, 'Configuration ID cannot be empty')
  .max(50, 'Configuration ID too long')
  .transform(str => PathValidator.validateConfigId(str));
```

**Protected Against:**
- Special characters that could be misinterpreted
- Overly long identifiers
- Case sensitivity issues
- Reserved words

### Content Size Limits

Strict limits are enforced on all content to prevent DoS attacks:

- Agent content: 50,000 characters max
- Command content: 50,000 characters max
- Hook content: 10,000 characters max
- Descriptions: 500 characters max
- File paths: 500 characters max

## File System Security

### Path Traversal Prevention

All file operations are protected against path traversal attacks:

```typescript
class PathValidator {
  static validatePath(inputPath: string): string {
    // Normalize the path
    const normalized = path.normalize(inputPath);
    
    // Reject paths that try to escape the working directory
    if (normalized.includes('..')) {
      throw new PathValidationError('Path traversal detected');
    }
    
    // Additional platform-specific validations...
  }
}
```

### File Permission Checks

- All file operations check permissions before execution
- Read-only files are never overwritten without explicit `--force` flag
- Backup files are created with secure permissions (0o600)

### Temporary File Security

- Temporary files are created in secure directories
- Temporary files are cleaned up automatically
- Backup files use timestamps to prevent collisions

### Directory Validation

```typescript
// Only allow creation in safe directories
const allowedDirectories = [
  '.claude',
  'agents',
  'commands', 
  'hooks'
];
```

## Configuration Security

### YAML/JSON Security

All configuration files are parsed safely:

```typescript
// Safe YAML parsing
try {
  const config = yaml.load(content, {
    schema: yaml.CORE_SCHEMA, // Restricted schema
    json: true, // JSON compatibility only
    onWarning: (warning) => {
      console.warn('YAML Warning:', warning);
    }
  });
} catch (error) {
  throw new ConfigurationError('Invalid YAML syntax');
}
```

**Protected Against:**
- YAML code injection
- Prototype pollution
- Resource exhaustion (large files)
- Circular references

### Frontmatter Security

Markdown frontmatter is parsed with strict validation:

```typescript
// Frontmatter is validated against schemas
const frontmatter = yaml.load(yamlContent, {
  schema: yaml.CORE_SCHEMA,
  json: true
});

// Then validated with Zod
const validatedFrontmatter = FrontmatterSchema.parse(frontmatter);
```

### Content Filtering

All configuration content is filtered for potentially dangerous patterns:

- No script tags in markdown content
- No external resource imports
- No executable content in non-hook files

## Dependency Security

### Optional Dependencies

Optional dependencies are loaded safely with fallbacks:

```typescript
let gradient: OptionalGradientString;

try {
  gradient = require('gradient-string');
} catch {
  // Safe fallback
  gradient = (text: string) => text;
}
```

### Dependency Validation

- All dependencies are pinned to specific versions
- Regular security audits using `npm audit`
- No dynamic imports or eval() usage
- TypeScript strict mode enabled

### Supply Chain Security

- All dependencies are from trusted sources
- Package-lock.json is committed and verified
- No postinstall scripts in dependencies
- Regular updates with security review

## Runtime Security

### Error Information Disclosure

Error messages are sanitized to prevent information disclosure:

```typescript
class ErrorHandler {
  static formatError(error: unknown): SafeErrorMessage {
    // Never expose internal paths or sensitive data
    if (error instanceof AppError) {
      return {
        message: error.message, // Pre-sanitized
        suggestions: this.getSafeSuggestions(error),
        code: error.code
      };
    }
    
    // Generic message for unknown errors
    return {
      message: 'An unexpected error occurred',
      suggestions: ['Please try again'],
      code: 'UNKNOWN_ERROR'
    };
  }
}
```

### Process Security

- No shell command execution
- No eval() or Function() usage
- No dynamic module loading
- Controlled file system access only

### Memory Security

- Bounded memory usage for large configurations
- Streaming for large file operations
- Automatic cleanup of temporary data
- No sensitive data in memory longer than necessary

## Configuration Best Practices

### For Configuration Authors

1. **Validate All Content**: Use the provided validation schemas
2. **Minimize Permissions**: Request only necessary permissions
3. **Sanitize Examples**: Ensure example code is safe
4. **Document Security**: Note any security considerations

### For End Users

1. **Review Configurations**: Always review before generating
2. **Use Dry Run**: Test with `--dry-run` first
3. **Backup Data**: Ensure important files are backed up
4. **Update Regularly**: Keep the tool updated

### For Developers

1. **Input Validation**: Always validate external input
2. **Error Handling**: Use the centralized error handler
3. **Type Safety**: Use TypeScript strictly
4. **Security Reviews**: Review PRs for security implications

## Security Checklist

Before using Claude Config Composer in production:

- [ ] Review all configurations being merged
- [ ] Verify file permissions in target directory
- [ ] Test with `--dry-run` flag first
- [ ] Ensure backup strategy is in place
- [ ] Check for any custom hooks or scripts
- [ ] Validate all configuration sources
- [ ] Review generated permissions in settings.json

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email security concerns to: [security@claudecomposer.dev]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### Response Timeline

- **24 hours**: Initial acknowledgment
- **72 hours**: Preliminary assessment
- **7 days**: Detailed analysis and fix timeline
- **30 days**: Public disclosure (if appropriate)

## Security Updates

Security updates are released as needed and follow this process:

1. **Critical**: Immediate patch release
2. **High**: Release within 72 hours
3. **Medium**: Release within 1 week
4. **Low**: Release with next scheduled update

Subscribe to security notifications:
- GitHub Security Advisories
- NPM Security Alerts
- Project releases

## Compliance

Claude Config Composer follows these security standards:

- **OWASP Top 10**: Protection against common vulnerabilities
- **NIST Guidelines**: Secure development practices
- **npm Security**: Regular dependency auditing
- **TypeScript Strict**: Type safety enforcement

## Additional Resources

- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [npm Security Guidelines](https://docs.npmjs.com/security/)
- [TypeScript Security](https://www.typescriptlang.org/docs/handbook/security.html)

---

**Remember**: Security is a shared responsibility. While Claude Config Composer implements strong security measures, users should always review configurations and follow security best practices in their own environments.