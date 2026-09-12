import chalk from 'chalk';
import fs from 'fs/promises';
import path from 'path';
import { ConfigGenerator } from '../../generator/config-generator';
import { ConfigRegistry } from '../../registry/config-registry';
import {
  ErrorHandler,
  FileSystemError,
  GenerationError,
  RegistryError,
  ValidationError,
} from '../../utils/error-handler';
import { InputValidator } from '../../utils/input-validator';
import { PathValidationError, PathValidator } from '../../utils/path-validator';
import { createSpinner } from '../../utils/simple-spinner';
import { BackupUtils } from '../utils/backup';
import { DisplayUtils } from '../utils/display';

export interface GenerateOptions {
  output?: string;
  backup?: boolean;
  gitignore?: boolean;
  fancy?: boolean;
}

/**
 * Generate command - generates configuration files from specified configs
 */
export class GenerateCommand {
  /**
   * Main generate command logic
   */
  static async execute(configs: string[], options: GenerateOptions): Promise<void> {
    await ErrorHandler.wrapAsync(async () => {
      // Validate input parameters
      await GenerateCommand.validateInputs(configs, options);

      const useFancy = Boolean(options.fancy && DisplayUtils.hasFancyVisuals);

      if (useFancy) {
        console.clear();
        DisplayUtils.showTitle(useFancy);
      }

      const registry = new ConfigRegistry();
      const spinner = createSpinner('Initializing registry...').start();

      try {
        await registry.initialize();
        spinner.succeed('Registry initialized');
      } catch (error) {
        spinner.fail('Failed to initialize registry');
        throw new RegistryError('Failed to load configuration registry', error as Error);
      }

      const generator = new ConfigGenerator();
      const configsToGenerate = [];
      const invalidConfigs: string[] = [];

      // Collect valid configurations
      for (const id of configs) {
        const metadata = registry.get(id);
        if (!metadata) {
          invalidConfigs.push(id);
          continue;
        }
        configsToGenerate.push({ path: metadata.path, metadata });
      }

      // Handle invalid configurations
      if (invalidConfigs.length > 0) {
        DisplayUtils.showInvalidConfigurations(invalidConfigs, registry.getAll());
      }

      if (configsToGenerate.length === 0) {
        console.error(chalk.red('\n❌ No valid configurations found to generate'));
        console.log(
          chalk.gray('\nRun "npx claude-config-composer list" to see all available configurations')
        );
        process.exit(1);
      }

      const targetDir = await GenerateCommand.getOutputDirectory(configs, options);

      // Backup existing configuration if needed (unless --no-backup)
      if (options.backup !== false && !targetDir.includes('.generated')) {
        await BackupUtils.backupExistingConfig(targetDir);
      }

      try {
        await GenerateCommand.ensureDirectory(targetDir);
        console.log(); // Add spacing before progress indicators
        await generator.generateCompleteConfig(configsToGenerate, targetDir, true);
      } catch (error) {
        throw new GenerationError(
          `Failed to generate configuration: ${error instanceof Error ? error.message : String(error)}`,
          error as Error
        );
      }

      // Ensure .claude/ is gitignored (unless --no-gitignore)
      if (options.gitignore !== false) {
        // Use targetDir to create the .gitignore in the correct location
        await BackupUtils.ensureGitignored('.claude', targetDir);
      }

      // Show success message and next steps
      DisplayUtils.showGenerationProgress(targetDir);
      DisplayUtils.showNextSteps(await GenerateCommand.isClaudeConfigRepo(), configs, targetDir);
    }, 'generate-command');
  }

  /**
   * Validate input parameters
   */
  private static async validateInputs(configs: string[], options: GenerateOptions): Promise<void> {
    try {
      if (!configs || configs.length === 0) {
        throw new ValidationError('Please specify configurations to combine');
      }

      // Validate the configs array and individual config IDs
      InputValidator.validateArrayBounds(configs, 1, 10, 'configuration');
      for (const config of configs) {
        if (typeof config !== 'string' || !config.trim()) {
          throw new ValidationError(`Configuration ID must be a non-empty string: "${config}"`);
        }
        PathValidator.validateConfigId(config);
      }

      // Validate output directory if provided
      if (options.output) {
        // Validate output path (allows absolute paths)
        PathValidator.validateOutputPath(options.output);
      }
    } catch (error) {
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError(
        `Invalid input: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error as Error
      );
    }
  }

  /**
   * Get the appropriate output directory
   */
  private static async getOutputDirectory(
    configs: string[],
    options: GenerateOptions
  ): Promise<string> {
    // Validate configs array
    try {
      InputValidator.validateArrayBounds(configs, 1, 10, 'configuration');
      configs.forEach(config => {
        if (typeof config !== 'string' || !config.trim()) {
          throw new Error('Configuration ID must be a non-empty string');
        }
        // Validate each config ID
        PathValidator.validateConfigId(config);
      });
    } catch (error) {
      throw new ValidationError(
        `Invalid configuration list: ${error instanceof Error ? error.message : 'Unknown error'}`,
        error as Error
      );
    }

    // If explicit output is provided, validate and use it
    if (options.output) {
      try {
        return PathValidator.validateOutputPath(options.output);
      } catch (error) {
        throw new ValidationError(
          `Invalid output directory: ${error instanceof PathValidationError ? error.message : 'Unknown error'}`,
          error as Error
        );
      }
    }

    // Check if we're in the claude-config-composer repo (testing mode)
    if (await GenerateCommand.isClaudeConfigRepo()) {
      const configName = configs.join('-');
      const testPath = path.join('.test-output', configName);
      return PathValidator.validateOutputPath(testPath);
    }

    // Default: output to current directory (production use)
    // This will create CLAUDE.md and .claude/ in the current directory
    return '.';
  }

  /**
   * Check if we're in the claude-config-composer repo asynchronously
   */
  private static async isClaudeConfigRepo(): Promise<boolean> {
    try {
      // Use relative path to avoid process.cwd() issues in CI
      const packageJson = await fs.readFile('package.json', 'utf-8');
      const pkg = JSON.parse(packageJson);
      return pkg.name === 'claude-config-composer';
    } catch {
      return false;
    }
  }

  /**
   * Ensure directory exists
   */
  private static async ensureDirectory(dirPath: string): Promise<void> {
    try {
      // Handle current directory case specially
      if (dirPath === '.') {
        // Current directory always exists, no need to create it
        return;
      }

      // Validate the directory path before creating
      const validatedPath = PathValidator.validateOutputPath(dirPath);
      if (validatedPath) {
        // Resolve the path relative to current working directory
        const resolvedPath = path.resolve(validatedPath);
        await fs.mkdir(resolvedPath, { recursive: true });
      }
    } catch (error) {
      if (error instanceof PathValidationError) {
        throw new ValidationError(`Invalid directory path: ${error.message}`, error);
      } else {
        throw new FileSystemError(`Failed to create directory: ${dirPath}`, error as Error);
      }
    }
  }
}
