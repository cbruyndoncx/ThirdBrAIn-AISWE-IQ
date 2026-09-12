import chalk from 'chalk';
import type {
  OptionalBoxen,
  OptionalCFonts,
  OptionalGradientString,
  OptionalNodeEmoji,
} from '../../types/optional-deps';

// Try to load fancy visual dependencies if available
let hasVisuals = false;
let _gradient: OptionalGradientString;
let CFonts: OptionalCFonts;
let boxen: OptionalBoxen;
let _emoji: OptionalNodeEmoji;

try {
  _gradient = require('gradient-string');
  CFonts = require('cfonts');
  boxen = require('boxen');
  _emoji = require('node-emoji');
  hasVisuals = true;
} catch {
  // Optional dependencies not available, use basic mode
}

export const CONFIG_CATEGORIES = {
  framework: '🏗️  Framework',
  ui: '🎨  UI/Styling',
  tooling: '⚙️  Tooling',
  database: '💾  Database',
  'mcp-server': '🔌  MCP Server',
};

/**
 * Display utilities for CLI output
 */
export class DisplayUtils {
  /**
   * Check if fancy visuals are available
   */
  static get hasFancyVisuals(): boolean {
    return hasVisuals;
  }

  /**
   * Show application title with optional fancy styling
   */
  static showTitle(fancy: boolean = false): void {
    if (fancy && hasVisuals && CFonts) {
      CFonts.say('Claude|Composer', {
        font: 'block',
        align: 'center',
        colors: ['red', 'white'],
        background: 'transparent',
        letterSpacing: 1,
        lineHeight: 1,
        space: true,
        maxLength: 0,
        gradient: true,
        independentGradient: true,
        transitionGradient: true,
      });
    } else {
      console.log(chalk.cyan.bold('\n🚀 Claude Config Composer\n'));
      console.log(chalk.gray('Generate custom Claude Code configurations for your stack\n'));
    }
  }

  /**
   * Show success message with fancy box if available
   */
  static showSuccessBox(targetDir: string, fancy: boolean = false): void {
    const displayPath = targetDir === '.' ? 'current directory' : targetDir;

    if (fancy && hasVisuals && boxen) {
      const boxText = boxen(
        `Complete configuration created in ${displayPath}\n\n` +
          `📄 CLAUDE.md          # Main configuration\n` +
          `📁 .claude/\n` +
          `├── ⚙️  settings.json  # Permissions & settings\n` +
          `├── 🤖 agents/        # AI assistants\n` +
          `├── 💻 commands/      # Custom commands\n` +
          `└── 🔧 hooks/         # Automation scripts`,
        {
          padding: 1,
          margin: 1,
          borderStyle: 'round',
          borderColor: 'green',
        }
      );
      console.log(boxText);
    } else {
      console.log(chalk.green(`\n✅ Complete configuration created in ${displayPath}`));
      DisplayUtils.showBasicStructure();
    }
  }

  /**
   * Show basic configuration structure
   */
  static showBasicStructure(): void {
    console.log(chalk.gray('\nStructure created:'));
    console.log(`  📄 CLAUDE.md          # Main configuration`);
    console.log(`  📁 .claude/`);
    console.log(`  ├── ⚙️  settings.json  # Permissions & settings`);
    console.log(`  ├── 🤖 agents/        # AI assistants`);
    console.log(`  ├── 💻 commands/      # Custom commands`);
    console.log(`  └── 🔧 hooks/         # Automation scripts`);
  }

  /**
   * Show configuration summary
   */
  static showConfigurationSummary(
    configs: Array<{ name: string; category: string }>,
    title: string = '📦 Selected configurations:'
  ): void {
    console.log(chalk.cyan(`\n${title}`));
    configs.forEach(config => {
      console.log(`  • ${config.name} (${config.category})`);
    });
  }

  /**
   * Show validation results
   */
  static showValidationResults(
    targetPath: string,
    validation: { valid: boolean; errors: string[] },
    agentCount?: number,
    commandCount?: number,
    hookCount?: number
  ): void {
    console.log(chalk.cyan(`\n🔍 Validating configuration in ${targetPath}...\n`));

    if (validation.valid) {
      console.log(chalk.green('✅ Configuration is valid!'));

      if (agentCount !== undefined && commandCount !== undefined && hookCount !== undefined) {
        console.log(chalk.gray('\nConfiguration contents:'));
        console.log(chalk.gray(`  • ${agentCount} agents`));
        console.log(chalk.gray(`  • ${commandCount} commands`));
        console.log(chalk.gray(`  • ${hookCount} hooks`));
      }
    } else {
      console.log(chalk.red('❌ Configuration validation failed:\n'));
      validation.errors.forEach(error => {
        console.log(chalk.red(`  • ${error}`));
      });
    }
  }

  /**
   * Show compatibility issues
   */
  static showCompatibilityIssues(compatibility: {
    valid: boolean;
    conflicts: string[];
    missingDependencies: string[];
  }): void {
    if (!compatibility.valid) {
      console.log(chalk.yellow('\n⚠️  Compatibility issues detected:\n'));

      if (compatibility.conflicts.length > 0) {
        console.log(chalk.red('Conflicts:'));
        compatibility.conflicts.forEach(c => console.log(`  - ${c}`));
      }

      if (compatibility.missingDependencies.length > 0) {
        console.log(chalk.yellow('\nMissing dependencies:'));
        compatibility.missingDependencies.forEach(d => console.log(`  - ${d}`));
      }
    } else {
      console.log(chalk.green('\n✅ No compatibility issues detected'));
    }
  }

  /**
   * Show dry run preview
   */
  static showDryRunPreview(
    targetDir: string,
    configs: Array<{ name: string; version: string; category: string }>,
    compatibility: {
      valid: boolean;
      conflicts: string[];
      missingDependencies: string[];
    }
  ): void {
    console.log(chalk.cyan('\n📋 Dry Run - Configuration Preview\n'));
    console.log(
      chalk.white('Target directory:'),
      targetDir === '.' ? 'current directory' : targetDir
    );
    console.log(chalk.white('\nConfigurations to merge:'));
    configs.forEach(c => {
      console.log(`  • ${c.name} v${c.version} (${c.category})`);
    });

    console.log(chalk.white('\n📁 Files that would be created:'));
    console.log('  📄 CLAUDE.md');
    console.log('  📄 README.md');
    console.log('  📄 package.json');
    console.log('  📁 .claude/');
    console.log('     ├── settings.json');
    console.log('     ├── agents/     (specialized AI assistants)');
    console.log('     ├── commands/   (custom commands)');
    console.log('     └── hooks/      (automation scripts)');

    DisplayUtils.showCompatibilityIssues(compatibility);
  }

  /**
   * Show available configurations by category
   */
  static showAvailableConfigurations(
    getByCategory: (category: string) => Array<{
      id: string;
      name: string;
      version: string;
      description: string;
    }>
  ): void {
    console.log(chalk.cyan.bold('\n📚 Available Configurations\n'));

    for (const [categoryId, categoryName] of Object.entries(CONFIG_CATEGORIES)) {
      const configs = getByCategory(categoryId);
      if (configs.length === 0) continue;

      console.log(chalk.yellow(`\n${categoryName}`));
      configs.forEach(c => {
        console.log(
          `  • ${chalk.white(c.name)} ${chalk.gray(`v${c.version}`)} - ${chalk.dim(c.description)}`
        );
      });
    }
  }

  /**
   * Show generation progress
   */
  static showGenerationProgress(targetDir: string): void {
    // Check if targetDir is the current directory (either '.' or the actual cwd path)
    let displayPath = 'current directory';
    try {
      const cwd = process.cwd();
      if (targetDir !== '.' && targetDir !== cwd) {
        displayPath = targetDir;
      }
    } catch {
      // If process.cwd() fails, just use the targetDir as-is
      displayPath = targetDir === '.' ? 'current directory' : targetDir;
    }
    console.log(chalk.green(`✅ Configuration generated in ${displayPath}`));

    // Show what was created
    console.log(chalk.gray('\nCreated:'));
    console.log(chalk.gray('  📄 CLAUDE.md - Main configuration'));
    console.log(chalk.gray('  📁 .claude/ - Settings, agents, commands, hooks'));
  }

  /**
   * Show next steps based on context
   */
  static showNextSteps(isTestMode: boolean, configs: string[], targetDir: string = '.'): void {
    if (isTestMode) {
      console.log(chalk.gray('\n📝 This is a test generation. To use in a real project:'));
      console.log(chalk.gray('   1. Navigate to your project directory'));
      console.log(chalk.gray('   2. Run: npx claude-config-composer ' + configs.join(' ')));
    } else {
      console.log(chalk.cyan('\n🎉 Your Claude Code configuration is ready!'));

      if (targetDir === '.') {
        console.log(
          chalk.gray('   Claude Code will automatically detect and use this configuration.')
        );
      } else {
        console.log(chalk.gray(`   Make sure Claude Code can access the ${targetDir}/ directory.`));
      }
    }
  }

  /**
   * Show usage examples
   */
  static showUsageExamples(): void {
    console.log(chalk.gray('\nUsage examples:'));
    console.log(chalk.gray('  npx claude-config-composer nextjs-15 shadcn'));
    console.log(chalk.gray('  npx claude-config-composer list'));
  }

  /**
   * Show invalid configurations with available alternatives
   */
  static showInvalidConfigurations(
    invalidConfigs: string[],
    allConfigs: Array<{ id: string; description: string }>
  ): void {
    console.warn(chalk.yellow(`\n⚠️  Unknown configurations: ${invalidConfigs.join(', ')}`));
    console.log(chalk.gray('\nAvailable configurations:'));
    allConfigs.forEach(c => {
      console.log(chalk.gray(`  • ${c.id} - ${c.description}`));
    });
  }

  /**
   * Show dry run command suggestion
   */
  static showDryRunSuggestion(configs: string[], outputOption?: string): void {
    console.log(chalk.gray('\n💡 To generate this configuration, run:'));
    console.log(
      chalk.gray(
        `   npx claude-config-composer ${configs.join(' ')}${outputOption ? ` --output ${outputOption}` : ''}`
      )
    );
  }
}
