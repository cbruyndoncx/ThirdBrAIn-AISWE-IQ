import fs from 'fs/promises';
import yaml from 'js-yaml';
import path from 'path';
import type {
  BuildTools,
  CodeRules,
  ComponentPatterns,
  HooksConfig,
  ImportOrder,
  StatusLine,
  TestingFramework,
} from '../types/config';
import { ConfigurationError, ErrorHandler, FileSystemError } from '../utils/error-handler';

/**
 * Represents an AI agent configuration with specialized capabilities
 */
export interface Agent {
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

/**
 * Represents a custom command configuration
 */
export interface Command {
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

/**
 * Represents a hook configuration for automation
 */
export interface Hook {
  /** The hook name/filename */
  name: string;
  /** The type of hook - script for executable files, config for JSON hooks */
  type: 'script' | 'config';
  /** The hook content (script code or JSON configuration) */
  content: string;
  /** The source configuration this hook came from */
  source: string;
}

/**
 * Represents the settings configuration for Claude Code
 */
export interface Settings {
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

/**
 * Parses Claude Code configuration directories and extracts structured components
 *
 * This class handles the parsing of:
 * - Agent definitions from markdown files
 * - Command definitions from markdown files
 * - Hook scripts and configurations
 * - Settings from JSON files
 * - Main CLAUDE.md documentation
 *
 * @example
 * ```typescript
 * const parser = new ConfigParser();
 * const config = await parser.parseConfigDirectory('./my-config');
 * console.log(`Found ${config.agents.length} agents`);
 * ```
 */
export class ConfigParser {
  /**
   * Parses a complete configuration directory structure
   *
   * @param configPath - Path to the configuration directory to parse
   * @returns Promise resolving to parsed configuration components
   * @throws {FileSystemError} When the directory cannot be accessed
   * @throws {ConfigurationError} When configuration files have invalid format
   *
   * @example
   * ```typescript
   * const parser = new ConfigParser();
   * const config = await parser.parseConfigDirectory('./configurations/nextjs-15');
   *
   * // Access parsed components
   * config.agents.forEach(agent => console.log(agent.name));
   * config.commands.forEach(cmd => console.log(cmd.name));
   * ```
   */
  async parseConfigDirectory(configPath: string): Promise<{
    /** Parsed AI agent configurations */
    agents: Agent[];
    /** Parsed custom command configurations */
    commands: Command[];
    /** Parsed hook configurations */
    hooks: Hook[];
    /** Parsed settings configuration, null if not found */
    settings: Settings | null;
    /** Content of main CLAUDE.md file, null if not found */
    claudeMd: string | null;
    /** Dependencies extracted from package.json if present */
    dependencies?: {
      peerDependencies?: Record<string, string>;
      dependencies?: Record<string, string>;
      devDependencies?: Record<string, string>;
      engines?: Record<string, string>;
    };
  }> {
    return ErrorHandler.wrapAsync(async () => {
      const agents: Agent[] = [];
      const commands: Command[] = [];
      const hooks: Hook[] = [];
      let settings: Settings | null = null;
      let claudeMd: string | null = null;
      let dependencies: Record<string, string> | undefined;

      // Validate config path
      if (!configPath || typeof configPath !== 'string') {
        throw new ConfigurationError('Invalid configuration path provided');
      }

      try {
        await fs.access(configPath);
      } catch (error: unknown) {
        throw new FileSystemError(
          `Configuration directory not found: ${configPath}`,
          error instanceof Error ? error : undefined
        );
      }

      // Parse CLAUDE.md
      try {
        claudeMd = await fs.readFile(path.join(configPath, 'CLAUDE.md'), 'utf-8');
      } catch (error: unknown) {
        if (
          error instanceof Error &&
          'code' in error &&
          (error as NodeJS.ErrnoException).code !== 'ENOENT'
        ) {
          ErrorHandler.warn(
            new FileSystemError(`Could not read CLAUDE.md: ${error.message}`, error),
            'parse-claude-md'
          );
        }
        // CLAUDE.md might not exist, which is fine
      }

      // Parse package.json for dependency information (optional)
      try {
        const packageJsonContent = await fs.readFile(
          path.join(configPath, 'package.json'),
          'utf-8'
        );
        const packageJson = JSON.parse(packageJsonContent);
        dependencies = {
          peerDependencies: packageJson.peerDependencies,
          dependencies: packageJson.dependencies,
          devDependencies: packageJson.devDependencies,
          engines: packageJson.engines,
        };
      } catch (_error: unknown) {
        // package.json is optional, ignore if not found
      }

      const claudeDir = path.join(configPath, '.claude');

      try {
        await fs.access(claudeDir);
      } catch (error: unknown) {
        if (
          error instanceof Error &&
          'code' in error &&
          (error as NodeJS.ErrnoException).code === 'ENOENT'
        ) {
          // No .claude directory is valid for some configurations
          return { agents, commands, hooks, settings, claudeMd, dependencies };
        }
        throw new FileSystemError(
          `Cannot access .claude directory: ${error instanceof Error ? error.message : String(error)}`,
          error instanceof Error ? error : undefined
        );
      }

      // Parse settings.json
      try {
        const settingsContent = await fs.readFile(path.join(claudeDir, 'settings.json'), 'utf-8');
        try {
          settings = JSON.parse(settingsContent);
        } catch (parseError: unknown) {
          throw new ConfigurationError(
            `Invalid JSON in settings.json: ${parseError instanceof Error ? parseError.message : String(parseError)}`,
            parseError instanceof Error ? parseError : undefined
          );
        }
      } catch (error: unknown) {
        if (
          error instanceof Error &&
          'code' in error &&
          (error as NodeJS.ErrnoException).code !== 'ENOENT' &&
          !(error instanceof ConfigurationError)
        ) {
          ErrorHandler.warn(
            new FileSystemError(`Could not read settings.json: ${error.message}`, error),
            'parse-settings'
          );
        }
      }

      // Parse agents
      const agentsDir = path.join(claudeDir, 'agents');
      try {
        const agentFiles = await fs.readdir(agentsDir);
        for (const file of agentFiles) {
          if (!file.endsWith('.md')) continue;

          try {
            const content = await fs.readFile(path.join(agentsDir, file), 'utf-8');
            const agent = this.parseAgent(content, file, configPath);
            if (agent) agents.push(agent);
          } catch (error: unknown) {
            ErrorHandler.warn(
              new FileSystemError(
                `Could not read agent file ${file}: ${error instanceof Error ? error.message : String(error)}`,
                error instanceof Error ? error : undefined
              ),
              'parse-agent'
            );
          }
        }
      } catch (error: unknown) {
        if (
          error instanceof Error &&
          'code' in error &&
          (error as NodeJS.ErrnoException).code !== 'ENOENT'
        ) {
          ErrorHandler.warn(
            new FileSystemError(`Could not read agents directory: ${error.message}`, error),
            'parse-agents'
          );
        }
      }

      // Parse commands
      const commandsDir = path.join(claudeDir, 'commands');
      try {
        const commandFiles = await fs.readdir(commandsDir);
        for (const file of commandFiles) {
          if (!file.endsWith('.md')) continue;

          try {
            const content = await fs.readFile(path.join(commandsDir, file), 'utf-8');
            const command = this.parseCommand(content, file, configPath);
            if (command) commands.push(command);
          } catch (error: unknown) {
            ErrorHandler.warn(
              new FileSystemError(
                `Could not read command file ${file}: ${error instanceof Error ? error.message : String(error)}`,
                error instanceof Error ? error : undefined
              ),
              'parse-command'
            );
          }
        }
      } catch (error: unknown) {
        if (
          error instanceof Error &&
          'code' in error &&
          (error as NodeJS.ErrnoException).code !== 'ENOENT'
        ) {
          ErrorHandler.warn(
            new FileSystemError(`Could not read commands directory: ${error.message}`, error),
            'parse-commands'
          );
        }
      }

      // Parse hooks
      const hooksDir = path.join(claudeDir, 'hooks');
      try {
        const hookFiles = await fs.readdir(hooksDir);
        for (const file of hookFiles) {
          try {
            const content = await fs.readFile(path.join(hooksDir, file), 'utf-8');

            if (file.endsWith('.json')) {
              // Validate JSON hooks
              try {
                JSON.parse(content);
                hooks.push({
                  name: file,
                  type: 'config',
                  content,
                  source: configPath,
                });
              } catch (parseError: unknown) {
                ErrorHandler.warn(
                  new ConfigurationError(
                    `Invalid JSON in hook file ${file}: ${parseError instanceof Error ? parseError.message : String(parseError)}`,
                    parseError instanceof Error ? parseError : undefined
                  ),
                  'parse-hook-json'
                );
              }
            } else if (file.endsWith('.sh') || file.endsWith('.js')) {
              hooks.push({
                name: file,
                type: 'script',
                content,
                source: configPath,
              });
            }
          } catch (error: unknown) {
            ErrorHandler.warn(
              new FileSystemError(
                `Could not read hook file ${file}: ${error instanceof Error ? error.message : String(error)}`,
                error instanceof Error ? error : undefined
              ),
              'parse-hook'
            );
          }
        }
      } catch (error: unknown) {
        if (
          error instanceof Error &&
          'code' in error &&
          (error as NodeJS.ErrnoException).code !== 'ENOENT'
        ) {
          ErrorHandler.warn(
            new FileSystemError(`Could not read hooks directory: ${error.message}`, error),
            'parse-hooks'
          );
        }
      }

      return { agents, commands, hooks, settings, claudeMd, dependencies };
    }, 'parse-config-directory');
  }

  private parseAgent(content: string, filename: string, source: string): Agent | null {
    try {
      if (!content || typeof content !== 'string') {
        throw new ConfigurationError(`Invalid content for agent ${filename}`);
      }

      const lines = content.split('\n');
      let frontmatterEnd = -1;

      // Find YAML frontmatter
      if (lines[0] === '---') {
        for (let i = 1; i < lines.length; i++) {
          if (lines[i] === '---') {
            frontmatterEnd = i;
            break;
          }
        }
      }

      let metadata: Record<string, unknown> = {};
      let bodyContent = content;

      if (frontmatterEnd > 0) {
        const frontmatter = lines.slice(1, frontmatterEnd).join('\n');
        try {
          metadata = yaml.load(frontmatter) as Record<string, unknown>;
          if (!metadata || typeof metadata !== 'object') {
            metadata = {};
          }
        } catch (yamlError: unknown) {
          throw new ConfigurationError(
            `Invalid YAML frontmatter in agent ${filename}: ${yamlError instanceof Error ? yamlError.message : String(yamlError)}`,
            yamlError instanceof Error ? yamlError : undefined
          );
        }
        bodyContent = lines.slice(frontmatterEnd + 1).join('\n');
      }

      // Handle tools - could be string or array
      let tools: string[] = [];
      if (metadata.tools) {
        if (typeof metadata.tools === 'string') {
          tools = metadata.tools
            .split(',')
            .map((t: string) => t.trim())
            .filter(t => t.length > 0);
        } else if (Array.isArray(metadata.tools)) {
          tools = metadata.tools.filter(t => typeof t === 'string' && t.trim().length > 0);
        } else {
          ErrorHandler.warn(
            new ConfigurationError(`Invalid tools format in agent ${filename}`),
            'parse-agent-tools'
          );
        }
      }

      const agent: Agent = {
        name: String(metadata.name || filename.replace('.md', '')),
        description: String(metadata.description || ''),
        tools,
        content: bodyContent.trim(),
        source,
      };

      // Validate required fields
      if (!agent.name.trim()) {
        throw new ConfigurationError(`Agent ${filename} must have a name`);
      }

      return agent;
    } catch (error) {
      if (error instanceof ConfigurationError) {
        ErrorHandler.warn(error, 'parse-agent');
      } else {
        ErrorHandler.warn(
          new ConfigurationError(
            `Error parsing agent ${filename}: ${error instanceof Error ? error.message : String(error)}`,
            error as Error
          ),
          'parse-agent'
        );
      }
      return null;
    }
  }

  private parseCommand(content: string, filename: string, source: string): Command | null {
    try {
      if (!content || typeof content !== 'string') {
        throw new ConfigurationError(`Invalid content for command ${filename}`);
      }

      const lines = content.split('\n');
      let frontmatterEnd = -1;

      // Find YAML frontmatter
      if (lines[0] === '---') {
        for (let i = 1; i < lines.length; i++) {
          if (lines[i] === '---') {
            frontmatterEnd = i;
            break;
          }
        }
      }

      let metadata: Record<string, unknown> = {};
      let bodyContent = content;

      if (frontmatterEnd > 0) {
        const frontmatter = lines.slice(1, frontmatterEnd).join('\n');
        try {
          metadata = yaml.load(frontmatter) as Record<string, unknown>;
          if (!metadata || typeof metadata !== 'object') {
            metadata = {};
          }
        } catch (yamlError: unknown) {
          throw new ConfigurationError(
            `Invalid YAML frontmatter in command ${filename}: ${yamlError instanceof Error ? yamlError.message : String(yamlError)}`,
            yamlError instanceof Error ? yamlError : undefined
          );
        }
        bodyContent = lines.slice(frontmatterEnd + 1).join('\n');
      }

      // Handle allowed-tools - could be string or array
      let allowedTools: string[] = [];
      if (metadata['allowed-tools']) {
        if (typeof metadata['allowed-tools'] === 'string') {
          allowedTools = metadata['allowed-tools']
            .split(',')
            .map((t: string) => t.trim())
            .filter(t => t.length > 0);
        } else if (Array.isArray(metadata['allowed-tools'])) {
          allowedTools = metadata['allowed-tools'].filter(
            t => typeof t === 'string' && t.trim().length > 0
          );
        } else {
          ErrorHandler.warn(
            new ConfigurationError(`Invalid allowed-tools format in command ${filename}`),
            'parse-command-tools'
          );
        }
      }

      const command: Command = {
        name: String(metadata.name || filename.replace('.md', '')),
        description: String(metadata.description || ''),
        allowedTools,
        argumentHint: String(metadata['argument-hint'] || ''),
        content: bodyContent.trim(),
        source,
      };

      // Validate required fields
      if (!command.name.trim()) {
        throw new ConfigurationError(`Command ${filename} must have a name`);
      }

      return command;
    } catch (error) {
      if (error instanceof ConfigurationError) {
        ErrorHandler.warn(error, 'parse-command');
      } else {
        ErrorHandler.warn(
          new ConfigurationError(
            `Error parsing command ${filename}: ${error instanceof Error ? error.message : String(error)}`,
            error as Error
          ),
          'parse-command'
        );
      }
      return null;
    }
  }
}
