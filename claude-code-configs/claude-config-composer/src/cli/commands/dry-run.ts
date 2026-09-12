import chalk from 'chalk';
import { ConfigRegistry } from '../../registry/config-registry';
import { ErrorHandler, RegistryError, ValidationError } from '../../utils/error-handler';
import { createSpinner } from '../../utils/simple-spinner';
import { DisplayUtils } from '../utils/display';

export interface DryRunOptions {
  output?: string;
}

/**
 * Dry-run command - previews what would be generated without creating files
 */
export class DryRunCommand {
  static async execute(configs: string[], options: DryRunOptions): Promise<void> {
    await ErrorHandler.wrapAsync(async () => {
      if (!configs || configs.length === 0) {
        throw new ValidationError('No configurations specified for dry run');
      }

      const registry = new ConfigRegistry();
      const spinner = createSpinner('Analyzing configurations...').start();

      try {
        await registry.initialize();
        spinner.succeed('Analysis complete');
      } catch (error) {
        spinner.fail('Failed to initialize registry');
        throw new RegistryError('Failed to load configuration registry', error as Error);
      }

      const targetDir = options.output || '.';
      const configsToGenerate = [];
      const invalidConfigs: string[] = [];

      // Validate and collect configurations
      for (const id of configs) {
        const metadata = registry.get(id);
        if (!metadata) {
          invalidConfigs.push(id);
          continue;
        }
        configsToGenerate.push(metadata);
      }

      // Show warnings for invalid configurations
      if (invalidConfigs.length > 0) {
        DisplayUtils.showInvalidConfigurations(invalidConfigs, registry.getAll());
      }

      // Check if we have any valid configurations
      if (configsToGenerate.length === 0) {
        console.error(chalk.red('\n❌ No valid configurations found'));
        process.exit(1);
      }

      // Check compatibility
      const compatibility = registry.validateCompatibility(configs);

      // Show the dry run preview
      DisplayUtils.showDryRunPreview(
        targetDir,
        configsToGenerate.map(c => ({
          name: c.name,
          version: c.version,
          category: c.category,
        })),
        compatibility
      );

      // Show command to actually generate
      DisplayUtils.showDryRunSuggestion(configs, options.output);
    }, 'dry-run-command');
  }
}
