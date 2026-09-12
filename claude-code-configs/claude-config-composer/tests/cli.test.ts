import { execSync } from 'child_process';
import fs from 'fs/promises';
import path from 'path';
import { beforeEach, describe, expect, it } from 'vitest';
import { TEST_TEMP_DIR } from './setup';

const CLI_PATH = path.resolve(__dirname, '../dist/cli.js');

describe('CLI Core Commands', () => {
  let testProjectDir: string;

  beforeEach(async () => {
    // Use unique directory for each test to avoid conflicts
    testProjectDir = path.join(
      TEST_TEMP_DIR,
      `test-project-${Date.now()}-${Math.random().toString(36).slice(2)}`
    );
    await fs.mkdir(testProjectDir, { recursive: true });

    // Create a basic package.json for the test project
    await fs.writeFile(
      path.join(testProjectDir, 'package.json'),
      JSON.stringify(
        {
          name: 'test-project',
          version: '1.0.0',
        },
        null,
        2
      )
    );
  });

  describe('list command', () => {
    it('should list all available configurations', () => {
      const output = execSync(`node ${CLI_PATH} list`, { encoding: 'utf-8' });

      expect(output).toContain('Available Configurations');
      expect(output).toContain('Framework');
      expect(output).toContain('Next.js 15');
      expect(output).toContain('UI/Styling');
      expect(output).toContain('shadcn/ui');
      expect(output).toContain('Tailwind CSS');
      expect(output).toContain('Database');
      expect(output).toContain('Drizzle ORM');
    });

    it('should display version information for each config', () => {
      const output = execSync(`node ${CLI_PATH} list`, { encoding: 'utf-8' });

      expect(output).toMatch(/v\d+\.\d+\.\d+/); // Version pattern
      expect(output).toContain('Next.js 15 with App Router');
      expect(output).toContain('Beautiful, accessible components');
    });
  });

  describe('dry-run command', () => {
    it('should preview configuration without creating files', async () => {
      const output = execSync(
        `node ${CLI_PATH} dry-run nextjs-15 shadcn --output "${testProjectDir}"`,
        {
          encoding: 'utf-8',
        }
      );

      expect(output).toContain('Dry Run - Configuration Preview');
      expect(output).toContain('Target directory: current directory');
      expect(output).toContain('Next.js 15');
      expect(output).toContain('shadcn/ui');
      expect(output).toContain('Files that would be created:');
      expect(output).toContain('CLAUDE.md');
      expect(output).toContain('.claude/');
      expect(output).toContain('No compatibility issues detected');

      // Verify no files were actually created
      const claudeDir = path.join(testProjectDir, '.claude');
      const claudeMd = path.join(testProjectDir, 'CLAUDE.md');

      await expect(fs.access(claudeDir)).rejects.toThrow();
      await expect(fs.access(claudeMd)).rejects.toThrow();
    });

    it('should detect invalid configuration names', () => {
      expect(() => {
        execSync(`node ${CLI_PATH} dry-run invalid-config --output "${testProjectDir}"`, {
          encoding: 'utf-8',
        });
      }).toThrow();
    });
  });

  describe('generate command', () => {
    it('should generate configuration files for single config', async () => {
      execSync(`node ${CLI_PATH} nextjs-15 --no-backup --output "${testProjectDir}"`, {
        encoding: 'utf-8',
      });

      // Check that files were created
      const claudeMd = await fs.readFile(path.join(testProjectDir, 'CLAUDE.md'), 'utf-8');
      const settingsJson = await fs.readFile(
        path.join(testProjectDir, '.claude', 'settings.json'),
        'utf-8'
      );

      expect(claudeMd).toContain('Next.js 15');
      expect(claudeMd).toContain('App Router');
      expect(JSON.parse(settingsJson)).toHaveProperty('permissions');

      // Check agents directory
      const agentsDir = await fs.readdir(path.join(testProjectDir, '.claude', 'agents'));
      expect(agentsDir.length).toBeGreaterThan(0);
      expect(agentsDir).toContain('nextjs-app-router.md');
    });

    it('should merge multiple configurations without conflicts', async () => {
      execSync(
        `node ${CLI_PATH} nextjs-15 shadcn tailwindcss --no-backup --output "${testProjectDir}"`,
        {
          encoding: 'utf-8',
        }
      );

      const claudeMd = await fs.readFile(path.join(testProjectDir, 'CLAUDE.md'), 'utf-8');
      const settingsJson = JSON.parse(
        await fs.readFile(path.join(testProjectDir, '.claude', 'settings.json'), 'utf-8')
      );

      // Check that all configs are mentioned
      expect(claudeMd).toContain('Next.js 15');
      expect(claudeMd).toContain('shadcn/ui');
      expect(claudeMd).toContain('Tailwind CSS');

      // Check merged settings
      expect(settingsJson.permissions).toBeDefined();
      expect(settingsJson.permissions.allow).toBeDefined();

      // Check that agents from all configs are present
      const agentsDir = await fs.readdir(path.join(testProjectDir, '.claude', 'agents'));
      expect(agentsDir).toContain('nextjs-app-router.md');
      expect(agentsDir).toContain('component-builder.md');
      // Tailwind CSS agent
      expect(agentsDir.some(f => f.includes('responsive'))).toBe(true);
    });

    it('should backup existing .claude directory', async () => {
      // Create existing .claude directory
      const claudeDir = path.join(testProjectDir, '.claude');
      await fs.mkdir(claudeDir, { recursive: true });
      await fs.writeFile(path.join(claudeDir, 'test.txt'), 'existing content');

      // Generate new config
      const output = execSync(`node ${CLI_PATH} nextjs-15 --output "${testProjectDir}"`, {
        encoding: 'utf-8',
      });

      // The output might say "Added .claude/ to .gitignore" instead in CI
      expect(output).toMatch(/Backing up existing configuration|Configuration generated/);

      // Check that backup was created
      const files = await fs.readdir(testProjectDir);
      const backupDir = files.find(f => f.includes('.backup-'));
      expect(backupDir).toBeDefined();

      // Verify backup contains original file
      const backupContent = await fs.readFile(
        path.join(testProjectDir, backupDir ?? '', 'test.txt'),
        'utf-8'
      );
      expect(backupContent).toBe('existing content');
    });

    it('should add .claude to .gitignore', async () => {
      // Create .gitignore
      await fs.writeFile(path.join(testProjectDir, '.gitignore'), 'node_modules/\n');

      execSync(`node ${CLI_PATH} nextjs-15 --output "${testProjectDir}"`, {
        encoding: 'utf-8',
      });

      const gitignore = await fs.readFile(path.join(testProjectDir, '.gitignore'), 'utf-8');

      expect(gitignore).toContain('.claude/');
      expect(gitignore).toContain('# Generated Claude Code configurations');
    });
  });

  describe('validate command', () => {
    it('should validate a properly generated configuration', async () => {
      // First generate a config
      execSync(`node ${CLI_PATH} nextjs-15 shadcn --no-backup --output "${testProjectDir}"`, {
        encoding: 'utf-8',
      });

      // Add delay for CI file system sync
      await new Promise(resolve => setTimeout(resolve, 500));

      // Then validate it
      const output = execSync(`node ${CLI_PATH} validate ${testProjectDir}`, { encoding: 'utf-8' });

      expect(output).toContain('Configuration is valid');
      expect(output).toContain('agents');
      expect(output).toContain('commands');
      expect(output).toContain('hooks');
    });

    it('should detect missing required files', async () => {
      // Create incomplete config
      const claudeDir = path.join(testProjectDir, '.claude');
      await fs.mkdir(claudeDir, { recursive: true });
      await fs.writeFile(
        path.join(claudeDir, 'settings.json'),
        JSON.stringify({ commands: {} }, null, 2)
      );

      expect(() => {
        execSync(`node ${CLI_PATH} validate ${testProjectDir}`, { encoding: 'utf-8' });
      }).toThrow();
    });

    it('should validate configurations directory structure', () => {
      const configurationsDir = path.resolve(__dirname, '../../configurations');
      const configs = ['frameworks/nextjs-15', 'ui/shadcn', 'ui/tailwindcss'];

      configs.forEach(config => {
        const output = execSync(
          `node ${CLI_PATH} validate ${path.join(configurationsDir, config)}`,
          { encoding: 'utf-8' }
        );

        expect(output).toContain('Configuration is valid');
      });
    });
  });

  describe('error handling', () => {
    it('should show helpful error for unknown commands', () => {
      try {
        execSync(`node ${CLI_PATH} unknown-command 2>&1`, { encoding: 'utf-8' });
        // Should not reach here - command should fail
        expect(true).toBe(false);
      } catch (error: unknown) {
        // Check that the error output contains helpful message
        const errorOutput =
          (error as Error & { stdout?: string; stderr?: string }).stdout ||
          (error as Error & { stdout?: string; stderr?: string }).stderr ||
          (error as Error).message ||
          '';
        expect(errorOutput).toMatch(/unknown|Usage:|error|invalid|no valid/i);
      }
    });

    it('should handle missing configuration gracefully', () => {
      expect(() => {
        execSync(`node ${CLI_PATH} non-existent-config --output "${testProjectDir}"`, {
          encoding: 'utf-8',
        });
      }).toThrow(/Unknown configuration/i);
    });

    it('should handle file system errors gracefully', () => {
      // Simply test that invalid paths are handled
      expect(() => {
        execSync(`node ${CLI_PATH} nextjs-15 --output /invalid/path/that/does/not/exist`, {
          encoding: 'utf-8',
        });
      }).toThrow();
    });
  });
});
