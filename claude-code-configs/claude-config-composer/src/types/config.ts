/**
 * Core configuration type definitions
 */

export interface StatusLine {
  type: 'command';
  command: string;
}

export interface CodeRules {
  eslint?: Record<string, unknown>;
  prettier?: Record<string, unknown>;
  typescript?: Record<string, unknown>;
  biome?: Record<string, unknown>;
}

export interface ComponentPatterns {
  directory?: string;
  naming?: 'camelCase' | 'PascalCase' | 'kebab-case' | 'snake_case';
  extension?: string;
  indexFiles?: boolean;
}

export interface ImportOrder {
  groups?: string[][];
  alphabetize?: {
    order?: 'asc' | 'desc';
    caseInsensitive?: boolean;
  };
}

export interface TestingFramework {
  framework?: 'vitest' | 'jest' | 'mocha' | 'cypress' | 'playwright';
  coverage?: boolean;
  setupFiles?: string[];
  testMatch?: string[];
}

export interface BuildTools {
  bundler?: 'webpack' | 'vite' | 'rollup' | 'esbuild' | 'turbopack';
  target?: string;
  optimization?: Record<string, unknown>;
}

export type HookCommand = {
  type: 'command';
  command: string;
  timeout?: number;
};

export type HookEntry = {
  matcher?: string;
  hooks: HookCommand[];
};

export interface HooksConfig {
  PreToolUse?: HookEntry[];
  PostToolUse?: HookEntry[];
  Stop?: HookEntry[];
  UserPromptSubmit?: HookEntry[];
  Notification?: HookEntry[];
  SubagentStop?: HookEntry[];
  SessionEnd?: HookEntry[];
  SessionStart?: HookEntry[];
  PreCompact?: HookEntry[];
  [hookName: string]: HookEntry[] | undefined;
}

export interface ConfigSettings {
  name?: string;
  description?: string;
  version?: string;
  statusLine?: StatusLine;
  codeRules?: CodeRules;
  componentPatterns?: ComponentPatterns;
  importOrder?: ImportOrder;
  testingFramework?: TestingFramework;
  buildTools?: BuildTools;
  hooks?: HooksConfig;
  [key: string]: unknown;
}

export interface ConfigComponent {
  type: 'agent' | 'command' | 'hook' | 'setting';
  name: string;
  content: string;
  metadata?: ConfigMetadata;
}

export interface PackageDependencies {
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
  peerDependencies?: Record<string, string>;
  optionalDependencies?: Record<string, string>;
  engines?: Record<string, string>;
}

export interface ConfigMetadata {
  title?: string;
  description?: string;
  version?: string;
  author?: string;
  tags?: string[];
  dependencies?: string[];
  optionalDependencies?: string[];
  category?: string;
  priority?: number;
  [key: string]: unknown;
}

export interface ParsedConfig {
  agents: ConfigComponent[];
  commands: ConfigComponent[];
  hooks: ConfigComponent[];
  settings: ConfigSettings;
  metadata?: ConfigMetadata;
}

export interface ConfigurationSource {
  path: string;
  name: string;
  description?: string;
  category?: 'frameworks' | 'ui' | 'databases' | 'tooling' | 'mcp-servers';
  tags?: string[];
}

export interface MergeOptions {
  overwriteConflicts?: boolean;
  preserveComments?: boolean;
  validateAfterMerge?: boolean;
  backupBeforeMerge?: boolean;
}

export interface GenerateOptions {
  outputDir: string;
  configurations: string[];
  mergeOptions?: MergeOptions;
  dryRun?: boolean;
  force?: boolean;
  verbose?: boolean;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  type: 'syntax' | 'semantic' | 'dependency' | 'conflict';
  message: string;
  location?: {
    file?: string;
    line?: number;
    column?: number;
  };
  severity: 'error' | 'warning' | 'info';
}

export interface ValidationWarning {
  type: 'deprecation' | 'performance' | 'best-practice';
  message: string;
  location?: {
    file?: string;
    line?: number;
    column?: number;
  };
}

export interface BackupInfo {
  timestamp: string;
  originalPath: string;
  backupPath: string;
  reason: string;
}

export interface OperationResult<T = unknown> {
  success: boolean;
  data?: T;
  errors?: string[];
  warnings?: string[];
  backups?: BackupInfo[];
}
