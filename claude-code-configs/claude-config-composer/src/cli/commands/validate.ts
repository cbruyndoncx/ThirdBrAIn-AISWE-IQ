import fs from 'fs/promises';
import path from 'path';
import { ConfigGenerator } from '../../generator/config-generator';
import { ErrorHandler, ValidationError } from '../../utils/error-handler';
import { DisplayUtils } from '../utils/display';

/**
 * Validate command - validates existing Claude Code configuration
 */
export class ValidateCommand {
  static async execute(configPath?: string): Promise<void> {
    await ErrorHandler.wrapAsync(async () => {
      const targetPath = configPath || '.';
      const generator = new ConfigGenerator();

      let validation: { valid: boolean; errors: string[] };
      let agentCount: number | undefined;
      let commandCount: number | undefined;
      let hookCount: number | undefined;

      try {
        validation = await generator.validateGeneratedStructure(targetPath);
      } catch (error) {
        throw new ValidationError(
          `Failed to validate configuration: ${error instanceof Error ? error.message : String(error)}`,
          error as Error
        );
      }

      // Get detailed information if validation passes
      if (validation.valid) {
        const claudeDir = path.join(targetPath, '.claude');

        try {
          await fs.access(claudeDir);
          const agentsDir = path.join(claudeDir, 'agents');
          const commandsDir = path.join(claudeDir, 'commands');
          const hooksDir = path.join(claudeDir, 'hooks');

          const countFiles = async (dir: string): Promise<number> => {
            try {
              await fs.access(dir);
              const files = await fs.readdir(dir);
              return files.length;
            } catch {
              return 0;
            }
          };

          agentCount = await countFiles(agentsDir);
          commandCount = await countFiles(commandsDir);
          hookCount = await countFiles(hooksDir);
        } catch {
          // Directory doesn't exist
        }
      }

      DisplayUtils.showValidationResults(
        targetPath,
        validation,
        agentCount,
        commandCount,
        hookCount
      );

      if (!validation.valid) {
        process.exit(1);
      }
    }, 'validate-command');
  }
}
