import { checkbox, confirm, select } from '@inquirer/prompts';
import chalk from 'chalk';
import { ConfigGenerator } from '../../generator/config-generator';
import { ConfigRegistry } from '../../registry/config-registry';
import { ErrorHandler, GenerationError, RegistryError } from '../../utils/error-handler';
import { createSpinner } from '../../utils/simple-spinner';
import { CONFIG_CATEGORIES, DisplayUtils } from '../utils/display';

export interface InteractiveOptions {
  fancy?: boolean;
}

/**
 * Interactive command - guided configuration selection and generation
 */
export class InteractiveCommand {
  static async execute(options: InteractiveOptions = {}): Promise<void> {
    await ErrorHandler.wrapAsync(async () => {
      const useFancy = Boolean(options.fancy && DisplayUtils.hasFancyVisuals);

      console.clear();
      DisplayUtils.showTitle(useFancy);

      const registry = new ConfigRegistry();
      const spinner = createSpinner('Loading available configurations...').start();

      try {
        await registry.initialize();
        spinner.succeed('Configurations loaded');
      } catch (error) {
        spinner.fail('Failed to load configurations');
        throw new RegistryError('Failed to load configuration registry', error as Error);
      }

      const mode = await select({
        message: 'How would you like to select your stack?',
        choices: [
          { name: 'Quick presets', value: 'presets' },
          { name: 'Custom selection', value: 'custom' },
          { name: 'By category', value: 'category' },
        ],
      });

      let selectedConfigs: string[] = [];

      if (mode === 'presets') {
        selectedConfigs = await InteractiveCommand.handlePresetSelection();
      } else if (mode === 'category') {
        selectedConfigs = await InteractiveCommand.handleCategorySelection(registry);
      } else {
        selectedConfigs = await InteractiveCommand.handleCustomSelection(registry);
      }

      // Validate compatibility and handle issues
      selectedConfigs = await InteractiveCommand.handleCompatibilityIssues(
        registry,
        selectedConfigs
      );

      // Show selected configurations
      const configObjects = selectedConfigs
        .map(id => registry.get(id))
        .filter(config => config !== null)
        .map(config => ({ name: config?.name || '', category: config?.category || 'unknown' }));

      DisplayUtils.showConfigurationSummary(configObjects);

      // Get output directory
      const targetDir = await InteractiveCommand.getOutputDirectory();

      // Generate configuration
      await InteractiveCommand.generateConfiguration(
        registry,
        selectedConfigs,
        targetDir,
        useFancy
      );
    }, 'interactive-command');
  }

  /**
   * Handle preset selection mode
   */
  private static async handlePresetSelection(): Promise<string[]> {
    const preset = await select({
      message: 'Choose a preset stack:',
      choices: [
        {
          name: 'Next.js 15 + shadcn/ui + Tailwind',
          value: ['nextjs-15', 'shadcn', 'tailwindcss'],
        },
        {
          name: 'Full-Stack Next.js (Complete)',
          value: ['nextjs-15', 'shadcn', 'tailwindcss', 'drizzle', 'vercel-ai-sdk'],
        },
        { name: 'AI Development Stack', value: ['vercel-ai-sdk', 'drizzle'] },
        { name: 'Memory MCP Server', value: ['memory-mcp-server'] },
        { name: 'Token-Gated MCP Server', value: ['token-gated-mcp-server'] },
      ],
    });
    return preset as string[];
  }

  /**
   * Handle category-based selection mode
   */
  private static async handleCategorySelection(registry: ConfigRegistry): Promise<string[]> {
    const selectedConfigs: string[] = [];

    for (const [categoryId, categoryName] of Object.entries(CONFIG_CATEGORIES)) {
      const configs = registry.getByCategory(categoryId);
      if (configs.length === 0) continue;

      const selected = await checkbox({
        message: `Select ${categoryName} configurations:`,
        choices: configs.map(c => ({
          name: `${c.name} (v${c.version})`,
          value: c.id,
          checked: false,
        })),
      });

      selectedConfigs.push(...selected);
    }

    return selectedConfigs;
  }

  /**
   * Handle custom selection mode
   */
  private static async handleCustomSelection(registry: ConfigRegistry): Promise<string[]> {
    const allConfigs = registry.getAll();
    return await checkbox({
      message: 'Select configurations to combine:',
      choices: allConfigs.map(c => ({
        name: `${c.name} - ${c.description}`,
        value: c.id,
        checked: false,
      })),
      required: true,
    });
  }

  /**
   * Handle compatibility issues and resolve them interactively
   */
  private static async handleCompatibilityIssues(
    registry: ConfigRegistry,
    selectedConfigs: string[]
  ): Promise<string[]> {
    const compatibility = registry.validateCompatibility(selectedConfigs);

    if (!compatibility.valid) {
      console.log(chalk.yellow('\n⚠️  Compatibility issues detected:\n'));

      if (compatibility.conflicts.length > 0) {
        console.log(chalk.red('Conflicts:'));
        compatibility.conflicts.forEach(c => console.log(`  - ${c}`));
      }

      if (compatibility.missingDependencies.length > 0) {
        console.log(chalk.yellow('\nMissing dependencies:'));
        compatibility.missingDependencies.forEach(d => console.log(`  - ${d}`));

        const addDeps = await confirm({
          message: 'Would you like to add the missing dependencies?',
          default: true,
        });

        if (addDeps) {
          const deps = compatibility.missingDependencies
            .map(d => d.split(' requires ')[1])
            .filter((d, i, arr) => arr.indexOf(d) === i);
          selectedConfigs.push(...deps);
        }
      }

      if (compatibility.conflicts.length > 0) {
        const proceed = await confirm({
          message: 'There are conflicts. Continue anyway?',
          default: false,
        });

        if (!proceed) {
          console.log(chalk.gray('\nExiting...'));
          process.exit(0);
        }
      }
    }

    return selectedConfigs;
  }

  /**
   * Get output directory from user
   */
  private static async getOutputDirectory(): Promise<string> {
    const outputPath = await select({
      message: '\nWhere should the configuration be generated?',
      choices: [
        { name: 'Current directory (add to existing project)', value: '.' },
        { name: 'Custom directory', value: 'custom' },
      ],
    });

    let targetDir = '.';
    if (outputPath === 'custom') {
      console.log(chalk.gray('Enter path relative to current directory'));
      targetDir = 'claude-config'; // Default suggestion
    }

    return targetDir;
  }

  /**
   * Generate the final configuration
   */
  private static async generateConfiguration(
    registry: ConfigRegistry,
    selectedConfigs: string[],
    targetDir: string,
    useFancy: boolean
  ): Promise<void> {
    const generator = new ConfigGenerator();
    const configsToGenerate = [];

    for (const id of selectedConfigs) {
      const metadata = registry.get(id);
      if (!metadata) continue;
      configsToGenerate.push({ path: metadata.path, metadata });
    }

    try {
      // Ensure directory exists
      await import('fs/promises').then(fs => fs.mkdir(targetDir, { recursive: true }));

      console.log(chalk.cyan('\n🔧 Generating configuration...\n'));
      await generator.generateCompleteConfig(configsToGenerate, targetDir, true);
    } catch (error) {
      throw new GenerationError(
        `Failed to generate configuration: ${error instanceof Error ? error.message : String(error)}`,
        error as Error
      );
    }

    // Show success message
    DisplayUtils.showSuccessBox(targetDir, useFancy);

    console.log(chalk.cyan('\n🎉 Your Claude Code configuration is ready!'));
    DisplayUtils.showNextSteps(false, selectedConfigs, targetDir);
  }
}
