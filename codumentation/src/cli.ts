#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { discoverCodxTargets } from './discovery';
import { validateTarget, buildTarget } from './validator';
import { clearLog, getFailureStats, rotateSummaryLog } from './logger';
import { initCodumentation } from './init';

const program = new Command();

program
  .name('codumentation')
  .description('Auto-verifiable Markdown for documentation that cannot rot')
  .version('0.1.0');

program
  .command('validate')
  .description('Validate all documentation against the codebase (CI mode)')
  .action(async () => {
    console.log(chalk.blue('🔍 Discovering .codx targets...\n'));

    try {
      const targets = await discoverCodxTargets();

      if (targets.length === 0) {
        console.log(chalk.yellow('⚠️  No .codx directories found'));
        process.exit(0);
      }

      console.log(chalk.blue(`Found ${targets.length} target(s):\n`));
      targets.forEach(t => console.log(`  - ${t.targetFile}`));
      console.log();

      let allSuccess = true;

      for (const target of targets) {
        console.log(chalk.blue(`Validating ${target.targetFile}...`));

        const result = await validateTarget(target);

        if (result.success && result.contentMatches) {
          console.log(chalk.green(`✓ ${target.targetFile} is valid and up-to-date\n`));
        } else {
          allSuccess = false;

          if (!result.success) {
            console.log(chalk.red(`✗ ${target.targetFile} validation failed:\n`));

            // Print failed validations
            for (const vr of result.validationResults) {
              if (!vr.success) {
                console.log(chalk.red(`  Module '${vr.moduleName}' failed:`));
                console.log(chalk.gray(`    ${vr.error}`));
                if (vr.errorContent) {
                  console.log(chalk.yellow(`\n    ${vr.errorContent}\n`));
                }
              }
            }
          } else if (!result.contentMatches) {
            console.log(chalk.red(`✗ ${target.targetFile} is out of sync with its .codx definition`));
            console.log(chalk.yellow(`  Run 'codumentation build' to update\n`));
          }

          if (result.error) {
            console.log(chalk.red(`  Error: ${result.error}\n`));
          }
        }
      }

      if (allSuccess) {
        console.log(chalk.green.bold('\n✓ All documentation is valid!\n'));
        process.exit(0);
      } else {
        console.log(chalk.red.bold('\n✗ Validation failed!\n'));
        console.log(chalk.gray('Check .codumentation.log for details\n'));
        process.exit(1);
      }
    } catch (error) {
      console.error(chalk.red('\n✗ Fatal error:'));
      console.error(chalk.red(error instanceof Error ? error.message : String(error)));
      process.exit(1);
    }
  });

program
  .command('build')
  .description('Build/regenerate all documentation files')
  .action(async () => {
    console.log(chalk.blue('🔍 Discovering .codx targets...\n'));

    try {
      const targets = await discoverCodxTargets();

      if (targets.length === 0) {
        console.log(chalk.yellow('⚠️  No .codx directories found'));
        process.exit(0);
      }

      console.log(chalk.blue(`Found ${targets.length} target(s):\n`));
      targets.forEach(t => console.log(`  - ${t.targetFile}`));
      console.log();

      // Rotate log to prevent unbounded growth
      rotateSummaryLog();

      let allSuccess = true;

      for (const target of targets) {
        console.log(chalk.blue(`Building ${target.targetFile}...`));

        const result = await buildTarget(target);

        if (result.success) {
          console.log(chalk.green(`✓ ${target.targetFile} built successfully\n`));
        } else {
          allSuccess = false;
          console.log(chalk.red(`✗ ${target.targetFile} build failed:\n`));

          // Print failed validations
          for (const vr of result.validationResults) {
            if (!vr.success) {
              console.log(chalk.red(`  Module '${vr.moduleName}' failed:`));
              console.log(chalk.gray(`    ${vr.error}`));
              if (vr.errorContent) {
                console.log(chalk.yellow(`\n    ${vr.errorContent}\n`));
              }
            }
          }

          if (result.error) {
            console.log(chalk.red(`  Error: ${result.error}\n`));
          }
        }
      }

      if (allSuccess) {
        console.log(chalk.green.bold('\n✓ All documentation built successfully!\n'));
        process.exit(0);
      } else {
        console.log(chalk.red.bold('\n✗ Build failed!\n'));
        console.log(chalk.gray('Check .codumentation-summary.log for failure patterns\n'));
        process.exit(1);
      }
    } catch (error) {
      console.error(chalk.red('\n✗ Fatal error:'));
      console.error(chalk.red(error instanceof Error ? error.message : String(error)));
      process.exit(1);
    }
  });

program
  .command('stats')
  .description('Show validation failure statistics')
  .option('-d, --days <number>', 'Number of days to look back', '30')
  .action(async (options) => {
    try {
      const days = parseInt(options.days, 10);
      const stats = getFailureStats(days);

      if (stats.totalFailures === 0) {
        console.log(chalk.green('\n✓ No validation failures recorded!\n'));
        process.exit(0);
      }

      console.log(chalk.blue(`\nValidation Failure Statistics (Last ${days} days)`));
      console.log(chalk.blue('='.repeat(50)));
      console.log();

      console.log(chalk.bold(`Total Failures: ${stats.totalFailures}`));
      console.log();

      // Sort modules by failure count (descending)
      const moduleEntries = Object.entries(stats.byModule).sort((a, b) => b[1] - a[1]);

      console.log(chalk.bold('Failures by Module:'));
      for (const [moduleName, count] of moduleEntries) {
        const bar = '█'.repeat(Math.min(count, 40));

        let line = `  ${moduleName}: ${count} failures`;

        // Highlight frequently failing modules
        if (count > stats.totalFailures * 0.4) {
          line += chalk.red(' ← Improve guidance!');
        } else if (count > stats.totalFailures * 0.2) {
          line += chalk.yellow(' ← Consider improving');
        }

        console.log(line);
        console.log(chalk.gray(`    ${bar}`));
      }
      console.log();

      // Show suggestions for most frequently failing modules
      if (moduleEntries.length > 0 && moduleEntries[0][1] > stats.totalFailures * 0.3) {
        const topModule = moduleEntries[0][0];
        console.log(chalk.yellow.bold('Suggestion:'));
        console.log(chalk.yellow(`  "${topModule}" fails frequently. Consider:`));
        console.log(chalk.gray('    - Adding more examples to the content'));
        console.log(chalk.gray('    - Clarifying the errorContent message'));
        console.log(chalk.gray('    - Adding validation hints or warnings'));
        console.log();
      }

      console.log(chalk.gray(`Time range: ${stats.timeRange.start.toLocaleDateString()} to ${stats.timeRange.end.toLocaleDateString()}`));
      console.log();
    } catch (error) {
      console.error(chalk.red('\n✗ Error reading statistics:'));
      console.error(chalk.red(error instanceof Error ? error.message : String(error)));
      process.exit(1);
    }
  });

program
  .command('init <file>')
  .description('Initialize codumentation for a markdown file')
  .option('-f, --force', 'Overwrite existing .codx directory')
  .action(async (file, options) => {
    console.log(chalk.blue(`\n📝 Initializing codumentation for ${file}...\n`));

    try {
      const result = await initCodumentation(file, { force: options.force });

      console.log(chalk.green('✓ Codumentation initialized successfully!\n'));
      console.log(chalk.white('Created:'));
      console.log(chalk.gray(`  ${result.codxDir}/`));
      console.log(chalk.gray(`    - index.md (template)`));
      console.log(chalk.gray(`    - ${result.sections} section module(s)`));
      console.log(chalk.gray(`    - _meta.ts (adoption validator)`));
      console.log(chalk.gray(`  ${result.guideFile}`));
      console.log();
      console.log(chalk.yellow('Next steps:'));
      console.log(chalk.white('  1. Open each module in the .codx folder'));
      console.log(chalk.white('  2. Add meaningful validate() functions'));
      console.log(chalk.white('  3. Run `codumentation validate` to check your setup'));
      console.log();
      console.log(chalk.gray('See .codumentation-guide.md for example validation patterns.\n'));
    } catch (error) {
      console.error(chalk.red('\n✗ Initialization failed:'));
      console.error(chalk.red(error instanceof Error ? error.message : String(error)));
      process.exit(1);
    }
  });

program.parse();
