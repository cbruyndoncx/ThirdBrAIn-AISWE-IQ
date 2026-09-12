# Claude Config Composer API Reference

This document provides a comprehensive reference for the Claude Config Composer API.

## Table of Contents

- [Core Classes](#core-classes)
- [Configuration Interfaces](#configuration-interfaces)
- [Validation Utilities](#validation-utilities)
- [Error Handling](#error-handling)
- [Type Definitions](#type-definitions)

## Core Classes

### ConfigParser

Parses Claude Code configuration directories and extracts structured components.

```typescript
import { ConfigParser } from 'claude-config-composer';

const parser = new ConfigParser();
```

#### Methods

##### `parseConfigDirectory(configPath: string)`

Parses a complete configuration directory structure.

**Parameters:**
- `configPath` (string): Path to the configuration directory to parse

**Returns:** `Promise<ParsedConfig>`
- `agents`: Array of parsed AI agent configurations
- `commands`: Array of parsed custom command configurations  
- `hooks`: Array of parsed hook configurations
- `settings`: Parsed settings configuration (null if not found)
- `claudeMd`: Content of main CLAUDE.md file (null if not found)

**Throws:**
- `FileSystemError`: When the directory cannot be accessed
- `ConfigurationError`: When configuration files have invalid format

**Example:**
```typescript
const config = await parser.parseConfigDirectory('./configurations/nextjs-15');
console.log(`Found ${config.agents.length} agents`);
```

### ComponentMerger

Handles the intelligent merging of configuration components from multiple sources.

```typescript
import { ComponentMerger } from 'claude-config-composer';

const merger = new ComponentMerger();
```

#### Methods

##### `mergeAgents(agentGroups: Agent[][])`

Merges agent configurations with intelligent deduplication.

**Parameters:**
- `agentGroups`: Array of agent arrays from different configurations

**Returns:** `Agent[]` - Merged and deduplicated array of agents

**Example:**
```typescript
const merged = merger.mergeAgents([nextjsAgents, shadcnAgents]);
```

##### `mergeCommands(commandGroups: Command[][])`

Merges command configurations, with later commands overriding earlier ones.

**Parameters:**
- `commandGroups`: Array of command arrays from different configurations

**Returns:** `Command[]` - Merged array of commands

##### `mergeHooks(hookGroups: Hook[][])`

Merges hook configurations, with later hooks overriding earlier ones.

**Parameters:**
- `hookGroups`: Array of hook arrays from different configurations

**Returns:** `Hook[]` - Merged array of hooks

##### `mergeSettings(settingsArray: (Settings | null)[])`

Merges settings configurations with deep merging logic.

**Parameters:**
- `settingsArray`: Array of settings objects from different configurations

**Returns:** `Settings` - Merged settings object

##### `generateAgentFile(agent: Agent)`

Generates a markdown file content for an agent.

**Parameters:**
- `agent`: The agent configuration to generate content for

**Returns:** `string` - Formatted markdown content with YAML frontmatter

##### `generateCommandFile(command: Command)`

Generates a markdown file content for a command.

**Parameters:**
- `command`: The command configuration to generate content for

**Returns:** `string` - Formatted markdown content with YAML frontmatter

### ConfigRegistry

Manages the registry of available configurations with caching and validation.

```typescript
import { ConfigRegistry } from 'claude-config-composer';

const registry = new ConfigRegistry('./configurations');
```

#### Methods

##### `loadConfigurations()`

Loads and validates all configurations from the registry directory.

**Returns:** `Promise<void>`

**Throws:**
- `RegistryError`: When configurations cannot be loaded or validated

##### `getConfiguration(id: string)`

Retrieves a specific configuration by ID.

**Parameters:**
- `id`: The configuration identifier

**Returns:** `ConfigMetadata | undefined`

##### `getAllConfigurations()`

Gets all available configurations.

**Returns:** `ConfigMetadata[]`

##### `getByCategory(category: string)`

Gets configurations filtered by category.

**Parameters:**
- `category`: The category to filter by

**Returns:** `ConfigMetadata[]`

##### `validateCompatibility(configIds: string[])`

Validates compatibility between multiple configurations.

**Parameters:**
- `configIds`: Array of configuration IDs to check

**Returns:** `CompatibilityResult`

### ConfigGenerator

Main class for generating merged configurations.

```typescript
import { ConfigGenerator } from 'claude-config-composer';

const generator = new ConfigGenerator();
```

#### Methods

##### `generateConfiguration(options: GenerateOptions)`

Generates a merged configuration from multiple sources.

**Parameters:**
- `options`: Generation options including configurations, output directory, and flags

**Returns:** `Promise<OperationResult>`

## Configuration Interfaces

### Agent

Represents an AI agent configuration with specialized capabilities.

```typescript
interface Agent {
  /** The display name of the agent */
  name: string;
  /** A description of the agent's purpose and capabilities */
  description: string;
  /** Optional list of tools the agent can use */
  tools?: string[];
  /** The main content/prompt for the agent */
  content: string;
  /** The source configuration this agent came from */
  source: string;
}
```

### Command

Represents a custom command configuration.

```typescript
interface Command {
  /** The command name (without prefix) */
  name: string;
  /** A description of what the command does */
  description: string;
  /** Optional list of tools the command is allowed to use */
  allowedTools?: string[];
  /** Optional hint about expected arguments */
  argumentHint?: string;
  /** The main content/instructions for the command */
  content: string;
  /** The source configuration this command came from */
  source: string;
}
```

### Hook

Represents a hook configuration for automation.

```typescript
interface Hook {
  /** The hook name/filename */
  name: string;
  /** The type of hook - script for executable files, config for JSON hooks */
  type: 'script' | 'config';
  /** The hook content (script code or JSON configuration) */
  content: string;
  /** The source configuration this hook came from */
  source: string;
}
```

### Settings

Represents the settings configuration for Claude Code.

```typescript
interface Settings {
  /** Legacy: List of allowed permissions */
  allow?: string[];
  /** Legacy: List of denied permissions */
  deny?: string[];
  /** Environment variables */
  env?: Record<string, string>;
  /** Hook configurations */
  hooks?: HooksConfig;
  /** Status line configuration */
  statusLine?: StatusLine;
  /** Code formatting and linting rules */
  codeRules?: CodeRules;
  /** Component organization patterns */
  componentPatterns?: ComponentPatterns;
  /** Import ordering rules */
  importOrder?: ImportOrder;
  /** Testing framework configuration */
  testingFramework?: TestingFramework;
  /** Build tools configuration */
  buildTools?: BuildTools;
  /** Modern permissions structure */
  permissions?: {
    allow?: string[];
    deny?: string[];
  };
  /** Additional configuration properties */
  [key: string]: unknown;
}
```

## Validation Utilities

### InputValidator

Provides comprehensive input validation using Zod schemas.

```typescript
import { InputValidator } from 'claude-config-composer';
```

#### Static Methods

##### `validateConfigMetadata(data: unknown)`

Validates configuration metadata against the schema.

**Parameters:**
- `data`: The data to validate

**Returns:** `ConfigMetadata` - Validated and typed configuration metadata

**Throws:** `ZodError` - When validation fails

##### `validateAgent(data: unknown)`

Validates agent configuration data.

**Parameters:**
- `data`: The agent data to validate

**Returns:** `Agent` - Validated agent configuration

##### `validateCommand(data: unknown)`

Validates command configuration data.

**Parameters:**
- `data`: The command data to validate

**Returns:** `Command` - Validated command configuration

##### `validateSettings(data: unknown)`

Validates settings configuration data.

**Parameters:**
- `data`: The settings data to validate

**Returns:** `Settings` - Validated settings configuration

##### `sanitizeUserInput(input: unknown)`

Sanitizes and validates user input safely.

**Parameters:**
- `input`: The user input to sanitize

**Returns:** `string` - Sanitized and validated string

**Throws:** `Error` - When input is invalid or contains unsafe characters

## Error Handling

### Error Classes

#### AppError

Base class for all application errors.

```typescript
abstract class AppError extends Error {
  abstract readonly code: string;
  abstract readonly statusCode: number;
}
```

#### ConfigurationError

Error for configuration-related issues.

```typescript
class ConfigurationError extends AppError {
  readonly code = 'CONFIG_ERROR';
  readonly statusCode = 1;
}
```

#### FileSystemError

Error for file system operations.

```typescript
class FileSystemError extends AppError {
  readonly code = 'FS_ERROR';
  readonly statusCode = 1;
}
```

#### ValidationError

Error for validation failures.

```typescript
class ValidationError extends AppError {
  readonly code = 'VALIDATION_ERROR';
  readonly statusCode = 1;
}
```

### ErrorHandler

Central error handler with recovery mechanisms.

```typescript
import { ErrorHandler } from 'claude-config-composer';
```

#### Static Methods

##### `handle(error: unknown, context?: string)`

Handle errors with appropriate user feedback and recovery suggestions.

**Parameters:**
- `error`: The error to handle
- `context`: Optional context information

**Returns:** `never` - This method exits the process

##### `warn(error: unknown, context?: string)`

Handle errors gracefully with warning instead of exit.

**Parameters:**
- `error`: The error to handle
- `context`: Optional context information

##### `wrapAsync<T>(operation: () => Promise<T>, context: string, fallback?: T)`

Wrap async operations with error handling.

**Parameters:**
- `operation`: The async operation to wrap
- `context`: Context for error reporting
- `fallback`: Optional fallback value

**Returns:** `Promise<T>` - The result of the operation or fallback

## Type Definitions

### GenerateOptions

Options for configuration generation.

```typescript
interface GenerateOptions {
  /** Output directory for generated configuration */
  outputDir: string;
  /** Array of configuration IDs to merge */
  configurations: string[];
  /** Merge options */
  mergeOptions?: MergeOptions;
  /** Whether to perform a dry run */
  dryRun?: boolean;
  /** Whether to force overwrite existing files */
  force?: boolean;
  /** Whether to enable verbose logging */
  verbose?: boolean;
}
```

### MergeOptions

Options for merging configurations.

```typescript
interface MergeOptions {
  /** Whether to overwrite conflicting files */
  overwriteConflicts?: boolean;
  /** Whether to preserve comments in merged files */
  preserveComments?: boolean;
  /** Whether to validate after merging */
  validateAfterMerge?: boolean;
  /** Whether to backup before merging */
  backupBeforeMerge?: boolean;
}
```

### OperationResult

Result of configuration operations.

```typescript
interface OperationResult<T = unknown> {
  /** Whether the operation succeeded */
  success: boolean;
  /** Optional result data */
  data?: T;
  /** Any errors that occurred */
  errors?: string[];
  /** Any warnings generated */
  warnings?: string[];
  /** Information about created backups */
  backups?: BackupInfo[];
}
```

## Usage Examples

### Basic Configuration Generation

```typescript
import { ConfigGenerator } from 'claude-config-composer';

const generator = new ConfigGenerator();

const result = await generator.generateConfiguration({
  outputDir: './my-project',
  configurations: ['nextjs-15', 'shadcn', 'drizzle'],
  force: false,
  verbose: true
});

if (result.success) {
  console.log('Configuration generated successfully!');
} else {
  console.error('Generation failed:', result.errors);
}
```

### Custom Configuration Parsing

```typescript
import { ConfigParser, ComponentMerger } from 'claude-config-composer';

const parser = new ConfigParser();
const merger = new ComponentMerger();

// Parse multiple configurations
const configs = await Promise.all([
  parser.parseConfigDirectory('./config1'),
  parser.parseConfigDirectory('./config2')
]);

// Merge components
const agents = merger.mergeAgents(configs.map(c => c.agents));
const commands = merger.mergeCommands(configs.map(c => c.commands));
const settings = merger.mergeSettings(configs.map(c => c.settings));

// Generate files
agents.forEach(agent => {
  const content = merger.generateAgentFile(agent);
  // Save to file...
});
```

### Validation and Error Handling

```typescript
import { InputValidator, ErrorHandler } from 'claude-config-composer';

try {
  const metadata = InputValidator.validateConfigMetadata({
    id: 'my-config',
    name: 'My Configuration',
    version: '1.0.0',
    description: 'A custom configuration',
    category: 'frameworks'
  });
  
  console.log('Validation passed:', metadata);
} catch (error) {
  ErrorHandler.warn(error, 'Configuration validation');
}
```

---

For more information and examples, see the [GitHub repository](https://github.com/Matt-Dionis/claude-code-configs).