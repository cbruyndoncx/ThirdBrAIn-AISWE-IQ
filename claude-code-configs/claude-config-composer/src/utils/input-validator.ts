import { z } from 'zod';
import {
  PathValidationError,
  PathValidator,
  validateConfigId as pathValidateConfigId,
  validateFilename as pathValidateFilename,
  validatePath as pathValidatePath,
} from './path-validator';

/**
 * Comprehensive input validation using Zod schemas
 * Provides type-safe validation for all user inputs
 */

/**
 * Custom Zod transforms and refinements for security
 */

// Safe string that doesn't contain null bytes or control characters
const SafeString = z
  .string()
  .min(1, 'String cannot be empty')
  .max(1000, 'String too long')
  .refine(
    str => !/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/.test(str),
    'String contains invalid control characters'
  );

// Long safe string for content fields
const SafeLongString = z
  .string()
  .min(1, 'String cannot be empty')
  .max(50000, 'String too long')
  .refine(
    str => !/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/.test(str),
    'String contains invalid control characters'
  );

// Configuration ID validation
const ConfigIdString = z
  .string()
  .min(1, 'Configuration ID cannot be empty')
  .max(50, 'Configuration ID too long')
  .transform(str => {
    try {
      return pathValidateConfigId(str);
    } catch (error) {
      throw new z.ZodError([
        {
          code: z.ZodIssueCode.custom,
          message:
            error instanceof PathValidationError ? error.message : 'Invalid configuration ID',
          path: [],
        },
      ]);
    }
  });

// File path validation for user-provided paths (relative paths only)
const FilePathString = z
  .string()
  .min(1, 'File path cannot be empty')
  .max(500, 'File path too long')
  .transform(str => {
    try {
      return pathValidatePath(str);
    } catch (error) {
      throw new z.ZodError([
        {
          code: z.ZodIssueCode.custom,
          message: error instanceof PathValidationError ? error.message : 'Invalid file path',
          path: [],
        },
      ]);
    }
  });

// Internal path validation for trusted system paths (can be absolute)
const InternalPathString = z
  .string()
  .min(1, 'Internal path cannot be empty')
  .max(500, 'Internal path too long')
  .transform(str => {
    try {
      return PathValidator.validateInternalPath(str);
    } catch (error) {
      throw new z.ZodError([
        {
          code: z.ZodIssueCode.custom,
          message: error instanceof PathValidationError ? error.message : 'Invalid internal path',
          path: [],
        },
      ]);
    }
  });

// Filename validation
const FilenameString = z
  .string()
  .min(1, 'Filename cannot be empty')
  .max(255, 'Filename too long')
  .transform(str => {
    try {
      return pathValidateFilename(str);
    } catch (error) {
      throw new z.ZodError([
        {
          code: z.ZodIssueCode.custom,
          message: error instanceof PathValidationError ? error.message : 'Invalid filename',
          path: [],
        },
      ]);
    }
  });

// Version string validation
const VersionString = z
  .string()
  .regex(/^\d+\.\d+\.\d+(?:-[a-zA-Z0-9-]+)?$/, 'Invalid version format (expected semver)');

// URL validation (for optional fields)
const UrlString = z
  .string()
  .url('Invalid URL format')
  .refine(
    url => ['http:', 'https:'].includes(new URL(url).protocol),
    'Only HTTP and HTTPS URLs are allowed'
  );

/**
 * Schema for configuration metadata validation
 */
export const ConfigMetadataSchema = z.object({
  id: ConfigIdString,
  name: SafeString.refine(str => str.length <= 100, 'Name too long'),
  version: VersionString,
  description: SafeString.refine(str => str.length <= 500, 'Description too long'),
  category: z.enum(['framework', 'ui', 'tooling', 'database', 'mcp-server']),
  path: InternalPathString,
  homepage: UrlString.optional(),
  repository: UrlString.optional(),
  author: SafeString.refine(str => str.length <= 100, 'Author name too long').optional(),
  license: SafeString.refine(str => str.length <= 50, 'License too long').optional(),
  keywords: z
    .array(SafeString.refine(str => str.length <= 50, 'Keyword too long'))
    .max(20)
    .optional(),
  dependencies: z
    .array(SafeString.refine(str => str.length <= 100, 'Dependency name too long'))
    .max(50)
    .optional(),
  peerDependencies: z
    .array(SafeString.refine(str => str.length <= 100, 'Peer dependency name too long'))
    .max(50)
    .optional(),
});

/**
 * Schema for CLI options validation
 */
export const CliOptionsSchema = z.object({
  output: FilePathString.optional(),
  config: z.array(ConfigIdString).min(1, 'At least one configuration must be specified').max(10),
  verbose: z.boolean().optional(),
  force: z.boolean().optional(),
  dryRun: z.boolean().optional(),
});

/**
 * Schema for agent configuration
 */
export const AgentSchema = z.object({
  name: SafeString.refine(str => str.length <= 100, 'Name too long'),
  description: SafeString.refine(str => str.length <= 500, 'Description too long'),
  tools: z
    .array(SafeString.refine(str => str.length <= 50, 'Tool name too long'))
    .max(20)
    .optional(),
  content: SafeLongString,
  source: SafeString.refine(str => str.length <= 500, 'Source path too long'),
});

/**
 * Schema for command configuration
 */
export const CommandSchema = z.object({
  name: SafeString.refine(str => str.length <= 100, 'Name too long'),
  description: SafeString.refine(str => str.length <= 500, 'Description too long'),
  arguments: z
    .array(SafeString.refine(str => str.length <= 100, 'Argument too long'))
    .max(10)
    .optional(),
  content: SafeLongString,
  source: SafeString.refine(str => str.length <= 500, 'Source path too long'),
});

/**
 * Schema for hook configuration
 */
export const HookSchema = z.object({
  name: FilenameString,
  description: SafeString.refine(str => str.length <= 500, 'Description too long').optional(),
  content: SafeLongString,
  source: SafeString.refine(str => str.length <= 500, 'Source path too long'),
  executable: z.boolean().optional(),
  triggers: z.array(z.enum(['pre-commit', 'post-commit', 'pre-push', 'post-merge'])).optional(),
});

/**
 * Schema for settings configuration
 */
export const SettingsSchema = z.object({
  permissions: z
    .object({
      allow: z.array(SafeString).optional(),
      deny: z.array(SafeString).optional(),
      readFiles: z.boolean().optional(),
      writeFiles: z.boolean().optional(),
      executeCommands: z.boolean().optional(),
      networkAccess: z.boolean().optional(),
    })
    .optional(),
  // Legacy allow/deny at root level
  allow: z.array(SafeString).optional(),
  deny: z.array(SafeString).optional(),
  tools: z
    .array(SafeString.refine(str => str.length <= 50, 'Tool name too long'))
    .max(50)
    .optional(),
  customInstructions: SafeString.refine(
    str => str.length <= 2000,
    'Instructions too long'
  ).optional(),
  workingDirectory: FilePathString.optional(),
  env: z
    .record(SafeString.refine(str => str.length <= 200, 'Environment value too long'))
    .optional(),
  environment: z
    .record(SafeString.refine(str => str.length <= 200, 'Environment value too long'))
    .optional(),
  hooks: z.any().optional(), // Complex structure, allow any for now
  statusLine: z
    .object({
      type: z.literal('command'),
      command: SafeString.refine(str => str.length <= 500, 'Command too long'),
    })
    .optional(),
  codeRules: z.any().optional(),
  componentPatterns: z.any().optional(),
  importOrder: z.any().optional(),
  testingFramework: z.any().optional(),
  buildTools: z.any().optional(),
  // Note: _metadata is removed as it's not part of the Claude Code settings.json schema
  // It was used internally for tracking but should not be in the final output
});

/**
 * Schema for complete configuration structure
 */
export const ConfigurationSchema = z.object({
  metadata: ConfigMetadataSchema,
  claudeMd: SafeString.refine(str => str.length <= 50000, 'Claude.md content too long').optional(),
  settings: SettingsSchema.optional(),
  agents: z.array(AgentSchema).max(50).optional(),
  commands: z.array(CommandSchema).max(100).optional(),
  hooks: z.array(HookSchema).max(20).optional(),
});

/**
 * Schema for file operation parameters
 */
export const FileOperationSchema = z.object({
  sourcePath: FilePathString,
  targetPath: FilePathString,
  basePath: FilePathString,
  overwrite: z.boolean().optional(),
  createDirectories: z.boolean().optional(),
});

/**
 * Schema for bulk configuration generation
 */
export const BulkGenerationSchema = z.object({
  configurations: z
    .array(
      z.object({
        path: FilePathString,
        metadata: ConfigMetadataSchema,
      })
    )
    .min(1)
    .max(10),
  outputDir: FilePathString,
  showProgress: z.boolean().optional(),
  validateOutput: z.boolean().optional(),
});

/**
 * Validation helper functions
 */
export class InputValidator {
  /**
   * Validates configuration metadata
   */
  static validateConfigMetadata(data: unknown): z.infer<typeof ConfigMetadataSchema> {
    return ConfigMetadataSchema.parse(data);
  }

  /**
   * Validates CLI options
   */
  static validateCliOptions(data: unknown): z.infer<typeof CliOptionsSchema> {
    return CliOptionsSchema.parse(data);
  }

  /**
   * Validates agent configuration
   */
  static validateAgent(data: unknown): z.infer<typeof AgentSchema> {
    return AgentSchema.parse(data);
  }

  /**
   * Validates command configuration
   */
  static validateCommand(data: unknown): z.infer<typeof CommandSchema> {
    return CommandSchema.parse(data);
  }

  /**
   * Validates hook configuration
   */
  static validateHook(data: unknown): z.infer<typeof HookSchema> {
    return HookSchema.parse(data);
  }

  /**
   * Validates settings configuration
   */
  static validateSettings(data: unknown): z.infer<typeof SettingsSchema> {
    return SettingsSchema.parse(data);
  }

  /**
   * Validates complete configuration
   */
  static validateConfiguration(data: unknown): z.infer<typeof ConfigurationSchema> {
    return ConfigurationSchema.parse(data);
  }

  /**
   * Validates file operation parameters
   */
  static validateFileOperation(data: unknown): z.infer<typeof FileOperationSchema> {
    return FileOperationSchema.parse(data);
  }

  /**
   * Validates bulk generation parameters
   */
  static validateBulkGeneration(data: unknown): z.infer<typeof BulkGenerationSchema> {
    return BulkGenerationSchema.parse(data);
  }

  /**
   * Validates an array with bounds checking
   */
  static validateArrayBounds<T>(
    array: T[],
    minLength: number = 0,
    maxLength: number = 1000,
    itemName: string = 'item'
  ): T[] {
    if (!Array.isArray(array)) {
      throw new Error(`Expected array, got ${typeof array}`);
    }

    if (array.length < minLength) {
      throw new Error(
        `Array must contain at least ${minLength} ${itemName}${minLength !== 1 ? 's' : ''}`
      );
    }

    if (array.length > maxLength) {
      throw new Error(
        `Array cannot contain more than ${maxLength} ${itemName}${maxLength !== 1 ? 's' : ''}`
      );
    }

    return array;
  }

  /**
   * Validates string length bounds
   */
  static validateStringBounds(
    str: string,
    minLength: number = 1,
    maxLength: number = 1000,
    fieldName: string = 'string'
  ): string {
    if (typeof str !== 'string') {
      throw new Error(`${fieldName} must be a string`);
    }

    if (str.length < minLength) {
      throw new Error(
        `${fieldName} must be at least ${minLength} character${minLength !== 1 ? 's' : ''} long`
      );
    }

    if (str.length > maxLength) {
      throw new Error(
        `${fieldName} cannot exceed ${maxLength} character${maxLength !== 1 ? 's' : ''}`
      );
    }

    return str;
  }

  /**
   * Validates numeric bounds
   */
  static validateNumericBounds(
    num: number,
    min: number = 0,
    max: number = Number.MAX_SAFE_INTEGER,
    fieldName: string = 'number'
  ): number {
    if (typeof num !== 'number' || !Number.isFinite(num)) {
      throw new Error(`${fieldName} must be a valid number`);
    }

    if (num < min) {
      throw new Error(`${fieldName} must be at least ${min}`);
    }

    if (num > max) {
      throw new Error(`${fieldName} cannot exceed ${max}`);
    }

    return num;
  }

  /**
   * Sanitizes and validates user input safely
   */
  static sanitizeUserInput(input: unknown): string {
    if (typeof input !== 'string') {
      throw new Error('Input must be a string');
    }

    // Remove null bytes and control characters
    const sanitized = input.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '');

    // Validate the sanitized string
    return SafeString.parse(sanitized);
  }
}

/**
 * Type exports for TypeScript users
 */
export type ConfigMetadata = z.infer<typeof ConfigMetadataSchema>;
export type CliOptions = z.infer<typeof CliOptionsSchema>;
export type Agent = z.infer<typeof AgentSchema>;
export type Command = z.infer<typeof CommandSchema>;
export type Hook = z.infer<typeof HookSchema>;
export type Settings = z.infer<typeof SettingsSchema>;
export type Configuration = z.infer<typeof ConfigurationSchema>;
export type FileOperation = z.infer<typeof FileOperationSchema>;
export type BulkGeneration = z.infer<typeof BulkGenerationSchema>;

/**
 * Convenience functions for common validations
 */
export function validateConfigId(configId: string): string {
  return ConfigIdString.parse(configId);
}

export function validateFilePath(filePath: string): string {
  return FilePathString.parse(filePath);
}

export function validateFilename(filename: string): string {
  return FilenameString.parse(filename);
}

export function validateVersion(version: string): string {
  return VersionString.parse(version);
}

export function validateUrl(url: string): string {
  return UrlString.parse(url);
}
