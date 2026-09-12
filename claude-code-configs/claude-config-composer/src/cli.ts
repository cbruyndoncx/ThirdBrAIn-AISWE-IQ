#!/usr/bin/env node

import { program } from 'commander';
import { DryRunCommand } from './cli/commands/dry-run';
import { GenerateCommand } from './cli/commands/generate';
import { InteractiveCommand } from './cli/commands/interactive';
import { ListCommand } from './cli/commands/list';
import { ValidateCommand } from './cli/commands/validate';
import { ErrorHandler } from './utils/error-handler';

const packageJson = require('../package.json');

/**
 * Main CLI orchestration layer
 *
 * This file serves as a thin orchestration layer that:
 * - Sets up the command-line interface using Commander.js
 * - Delegates command execution to specialized command modules
 * - Handles top-level error management
 * - Provides consistent command structure and help text
 */

// Set up the main program
program
  .name('claude-compose')
  .description('Generate custom Claude Code configurations for your development stack')
  .version(packageJson.version);

// Interactive command
program
  .command('interactive')
  .alias('i')
  .description('Interactive mode to select and compose configurations')
  .option('--fancy', 'Use fancy visual effects (if dependencies are available)')
  .action(async options => {
    try {
      await InteractiveCommand.execute(options);
    } catch (error) {
      ErrorHandler.handle(error, 'interactive');
    }
  });

// Main command - can be called directly with configs
program
  .argument('[configs...]', 'Configuration IDs to combine (e.g., nextjs-15 shadcn)')
  .option('-o, --output <dir>', 'Output directory (default: current directory)')
  .option('--no-backup', 'Skip backing up existing configuration')
  .option('--no-gitignore', 'Skip adding to .gitignore')
  .option('--fancy', 'Use fancy visual effects (if dependencies are available)')
  .action(async (configs: string[], options) => {
    try {
      // If no configs provided, fall back to interactive mode
      if (!configs || configs.length === 0) {
        await InteractiveCommand.execute(options);
      } else {
        // Otherwise, generate the config
        await GenerateCommand.execute(configs, options);
      }
    } catch (error) {
      ErrorHandler.handle(error, 'generate');
    }
  });

// List command
program
  .command('list')
  .alias('ls')
  .description('List available configurations')
  .action(async () => {
    try {
      await ListCommand.execute();
    } catch (error) {
      ErrorHandler.handle(error, 'list');
    }
  });

// Validate command
program
  .command('validate [path]')
  .description('Validate an existing Claude Code configuration')
  .action(async (configPath?: string) => {
    try {
      await ValidateCommand.execute(configPath);
    } catch (error) {
      ErrorHandler.handle(error, 'validate');
    }
  });

// Dry-run command
program
  .command('dry-run <configs...>')
  .description('Preview what would be generated without creating files')
  .option('-o, --output <dir>', 'Output directory (default: current directory)')
  .action(async (configs: string[], options) => {
    try {
      await DryRunCommand.execute(configs, options);
    } catch (error) {
      ErrorHandler.handle(error, 'dry-run');
    }
  });

// Global error handling for uncaught errors
process.on('uncaughtException', error => {
  ErrorHandler.handle(error, 'uncaught-exception');
});

process.on('unhandledRejection', reason => {
  ErrorHandler.handle(reason, 'unhandled-rejection');
});

// Parse command line arguments
program.parse();
