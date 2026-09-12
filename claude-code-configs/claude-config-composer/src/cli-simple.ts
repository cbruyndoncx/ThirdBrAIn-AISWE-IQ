#!/usr/bin/env node

/**
 * Simplified CLI for testing purposes
 * This file provides a minimal interface for CI testing
 */

import chalk from 'chalk';
import { program } from 'commander';
import { ConfigRegistry } from './registry/config-registry';

const packageJson = require('../package.json');

// Initialize registry
const registry = new ConfigRegistry();

// Immediately initialize the registry
(async () => {
  await registry.initialize();
})();

program
  .name('claude-compose')
  .description('Generate custom Claude Code configurations')
  .version(packageJson.version);

// List command
program
  .command('list')
  .description('List all available configurations')
  .action(async () => {
    // Ensure registry is initialized
    if (registry.getAll().length === 0) {
      await registry.initialize();
    }

    console.log(chalk.cyan.bold('\n📚 Available Configurations\n'));

    const categories = ['framework', 'ui', 'tooling', 'database', 'mcp-server'];

    categories.forEach(category => {
      const configs = registry.getByCategory(category);
      if (configs.length > 0) {
        console.log(chalk.yellow(`\n${category.toUpperCase()}`));
        configs.forEach(config => {
          console.log(
            `  • ${chalk.white(config.name)} ${chalk.gray(`v${config.version}`)} - ${chalk.dim(config.description)}`
          );
        });
      }
    });

    console.log();
  });

// Parse arguments
program.parse(process.argv);

// Show help if no command specified
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
