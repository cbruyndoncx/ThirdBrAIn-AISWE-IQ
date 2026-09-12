import chalk from 'chalk';

/**
 * Base class for all application errors
 */
export abstract class AppError extends Error {
  abstract readonly code: string;
  abstract readonly statusCode: number;

  constructor(
    message: string,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

/**
 * Error for configuration-related issues
 */
export class ConfigurationError extends AppError {
  readonly code = 'CONFIG_ERROR';
  readonly statusCode = 1;
}

/**
 * Error for registry/loading issues
 */
export class RegistryError extends AppError {
  readonly code = 'REGISTRY_ERROR';
  readonly statusCode = 1;
}

/**
 * Error for validation failures
 */
export class ValidationError extends AppError {
  readonly code = 'VALIDATION_ERROR';
  readonly statusCode = 1;
}

/**
 * Error for file system operations
 */
export class FileSystemError extends AppError {
  readonly code = 'FS_ERROR';
  readonly statusCode = 1;
}

/**
 * Error for user input issues
 */
export class UserInputError extends AppError {
  readonly code = 'INPUT_ERROR';
  readonly statusCode = 1;
}

/**
 * Error for generation/merging issues
 */
export class GenerationError extends AppError {
  readonly code = 'GENERATION_ERROR';
  readonly statusCode = 1;
}

/**
 * Central error handler with recovery mechanisms and user-friendly messages
 */
export class ErrorHandler {
  /**
   * Handle errors with appropriate user feedback and recovery suggestions
   */
  static handle(error: unknown, context?: string): never {
    const formattedError = ErrorHandler.formatError(error, context);

    console.error(formattedError.message);

    if (formattedError.suggestions.length > 0) {
      console.log(chalk.yellow('\n💡 Suggestions:'));
      formattedError.suggestions.forEach(suggestion => {
        console.log(chalk.yellow(`   • ${suggestion}`));
      });
    }

    if (formattedError.recovery.length > 0) {
      console.log(chalk.cyan('\n🔧 Recovery options:'));
      formattedError.recovery.forEach(option => {
        console.log(chalk.cyan(`   • ${option}`));
      });
    }

    // Don't exit during tests - throw error instead
    if (process.env.NODE_ENV === 'test' || process.env.VITEST === 'true') {
      throw error instanceof Error ? error : new Error(String(error));
    }

    process.exit(formattedError.exitCode);
  }

  /**
   * Handle errors gracefully with warning instead of exit
   */
  static warn(error: unknown, context?: string): void {
    const formattedError = ErrorHandler.formatError(error, context);

    console.warn(chalk.yellow(`⚠️  Warning: ${formattedError.message.replace(/❌.*?Error: /, '')}`));

    if (formattedError.suggestions.length > 0) {
      console.log(chalk.yellow('\n💡 Suggestions:'));
      formattedError.suggestions.forEach(suggestion => {
        console.log(chalk.yellow(`   • ${suggestion}`));
      });
    }
  }

  /**
   * Format error with appropriate styling and recovery suggestions
   */
  private static formatError(
    error: unknown,
    context?: string
  ): {
    message: string;
    suggestions: string[];
    recovery: string[];
    exitCode: number;
  } {
    const contextPrefix = context ? `[${context}] ` : '';

    if (error instanceof AppError) {
      return {
        message: chalk.red(`❌ ${contextPrefix}Error: ${error.message}`),
        suggestions: ErrorHandler.getSuggestionsForError(error),
        recovery: ErrorHandler.getRecoveryOptionsForError(error),
        exitCode: error.statusCode,
      };
    }

    if (error instanceof Error) {
      const appError = ErrorHandler.categorizeError(error);
      return {
        message: chalk.red(`❌ ${contextPrefix}Error: ${error.message}`),
        suggestions: ErrorHandler.getSuggestionsForError(appError),
        recovery: ErrorHandler.getRecoveryOptionsForError(appError),
        exitCode: 1,
      };
    }

    return {
      message: chalk.red(`❌ ${contextPrefix}Unknown error: ${String(error)}`),
      suggestions: ['Check the console for more details', 'Ensure all dependencies are installed'],
      recovery: ['Try running the command again', 'Check your environment setup'],
      exitCode: 1,
    };
  }

  /**
   * Categorize generic errors into specific error types
   */
  private static categorizeError(error: Error): AppError {
    const message = error.message.toLowerCase();

    if (message.includes('permission') || message.includes('eacces')) {
      return new FileSystemError('Permission denied. Check file/directory permissions.', error);
    }

    if (message.includes('enoent') || message.includes('not found')) {
      return new FileSystemError('File or directory not found.', error);
    }

    if (message.includes('enospc')) {
      return new FileSystemError('No space left on device.', error);
    }

    if (message.includes('invalid') || message.includes('malformed')) {
      return new ValidationError('Invalid input or configuration format.', error);
    }

    if (message.includes('network') || message.includes('fetch') || message.includes('timeout')) {
      return new RegistryError('Network or connectivity issue.', error);
    }

    if (message.includes('parse') || message.includes('json') || message.includes('yaml')) {
      return new ConfigurationError('Configuration file parsing error.', error);
    }

    // Default to ConfigurationError for uncategorized errors
    return new ConfigurationError(error.message, error);
  }

  /**
   * Get contextual suggestions based on error type
   */
  private static getSuggestionsForError(error: AppError): string[] {
    switch (error.code) {
      case 'FS_ERROR':
        if (error.message.includes('permission')) {
          return [
            'Run with appropriate permissions (sudo if necessary)',
            'Check if the target directory is writable',
            'Ensure the parent directory exists',
          ];
        }
        if (error.message.includes('not found')) {
          return [
            'Verify the path exists',
            'Use absolute paths instead of relative ones',
            'Check spelling of directory/file names',
          ];
        }
        return ['Check file system permissions and available space'];

      case 'CONFIG_ERROR':
        return [
          'Validate your configuration syntax',
          'Check for missing required fields',
          'Ensure all referenced files exist',
        ];

      case 'REGISTRY_ERROR':
        return [
          'Check your internet connection',
          'Verify the configuration registry is accessible',
          'Try again in a few moments',
        ];

      case 'VALIDATION_ERROR':
        return [
          'Check input format and syntax',
          'Ensure all required parameters are provided',
          'Verify configuration IDs are valid',
        ];

      case 'INPUT_ERROR':
        return [
          'Check command syntax and parameters',
          'Use --help to see available options',
          'Ensure configuration IDs are correct',
        ];

      case 'GENERATION_ERROR':
        return [
          'Check if target directory is writable',
          'Ensure sufficient disk space',
          'Verify configuration compatibility',
        ];

      default:
        return ['Check the documentation for troubleshooting steps'];
    }
  }

  /**
   * Get recovery options based on error type
   */
  private static getRecoveryOptionsForError(error: AppError): string[] {
    switch (error.code) {
      case 'FS_ERROR':
        return [
          'Try with a different output directory',
          'Check and fix file permissions',
          'Clear disk space if needed',
        ];

      case 'CONFIG_ERROR':
        return [
          'Use a different configuration combination',
          'Try the dry-run command first',
          'Generate a single configuration to test',
        ];

      case 'REGISTRY_ERROR':
        return [
          'Try again later',
          'Check network connectivity',
          'Use cached configurations if available',
        ];

      case 'VALIDATION_ERROR':
        return [
          'Run "list" command to see available configurations',
          'Use the interactive mode for guided selection',
          'Check the documentation for valid options',
        ];

      case 'INPUT_ERROR':
        return [
          'Use the interactive mode instead',
          'Run with --help for usage information',
          'Try simpler command options first',
        ];

      case 'GENERATION_ERROR':
        return [
          'Try generating to a different directory',
          'Use --no-backup to skip backup step',
          'Generate configurations individually',
        ];

      default:
        return [
          'Try the interactive mode for guided experience',
          'Check the documentation for examples',
          'Report the issue if it persists',
        ];
    }
  }

  /**
   * Wrap async operations with error handling
   */
  static async wrapAsync<T>(
    operation: () => Promise<T>,
    context: string,
    fallback?: T
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (fallback !== undefined) {
        ErrorHandler.warn(error, context);
        return fallback;
      }
      ErrorHandler.handle(error, context);
    }
  }

  /**
   * Wrap sync operations with error handling
   */
  static wrapSync<T>(operation: () => T, context: string, fallback?: T): T {
    try {
      return operation();
    } catch (error) {
      if (fallback !== undefined) {
        ErrorHandler.warn(error, context);
        return fallback;
      }
      ErrorHandler.handle(error, context);
    }
  }
}
