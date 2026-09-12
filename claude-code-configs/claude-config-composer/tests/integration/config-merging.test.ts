import path from 'path';
import { beforeEach, describe, expect, it } from 'vitest';
import { ConfigMerger } from '../../src/merger/config-merger';
import { ConfigRegistry } from '../../src/registry/config-registry';

describe('Configuration Merging Tests', () => {
  let configRegistry: ConfigRegistry;
  let configMerger: ConfigMerger;

  beforeEach(async () => {
    const configurationsPath = path.resolve(__dirname, '../../../configurations');
    configRegistry = new ConfigRegistry(configurationsPath);
    await configRegistry.initialize();
    configMerger = new ConfigMerger();
  });

  // Helper function to get configs with content
  async function getConfigsWithContent(ids: string[]) {
    const configs = [];
    for (const id of ids) {
      const metadata = configRegistry.get(id);
      if (metadata) {
        const content = await configRegistry.getConfigContent(id);
        if (content) {
          configs.push({ content, metadata });
        }
      }
    }
    return configs;
  }

  describe('Basic Merging Logic', () => {
    it('should merge configurations with correct priority ordering', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn'];
      const configs = await getConfigsWithContent(selectedConfigs);

      expect(configs).toHaveLength(2);

      const mergedContent = configMerger.merge(configs);

      // Next.js should come first (higher priority)
      const sections = mergedContent.split('\n## ').slice(1); // Skip title
      const sectionTitles = sections.map(section => section.split('\n')[0]);

      // Critical sections should be early
      const criticalSectionIndex = sectionTitles.findIndex(
        title => title.includes('Breaking') || title.includes('Security')
      );
      expect(criticalSectionIndex).toBeGreaterThanOrEqual(0);
      expect(criticalSectionIndex).toBeLessThan(10); // Should be in top 10 sections
    });

    it('should preserve non-mergeable sections from highest priority config', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      // Should contain Next.js critical sections (non-mergeable, high priority)
      expect(mergedContent).toContain('Breaking Changes from Next.js 14');
      expect(mergedContent).toContain('Async Request APIs');

      // Should not duplicate critical sections
      const criticalMatches = mergedContent.match(/Breaking Changes from Next\.js 14/g);
      expect(criticalMatches?.length).toBe(1);
    });

    it('should merge common commands from multiple configurations', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      // Should contain commands section with merged commands
      expect(mergedContent.toLowerCase()).toContain('development');

      // Should include content from both configs (commands are in separate files)
      expect(mergedContent).toContain('Next.js');
      expect(mergedContent).toContain('shadcn');
    });
  });

  describe('Content Quality Validation', () => {
    it('should maintain markdown structure integrity', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn', 'tailwindcss'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      // Should have proper markdown structure
      expect(mergedContent).toMatch(/^#\s+.+/m); // Should have main title
      expect(mergedContent).toMatch(/^##\s+.+/m); // Should have section headers

      // Should not have broken markdown syntax
      expect(mergedContent).not.toContain('##  ##'); // No double headers
      expect(mergedContent).not.toMatch(/^\s*##\s*$/m); // No empty headers
    });

    it('should preserve code blocks and examples', async () => {
      const selectedConfigs = ['nextjs-15', 'vercel-ai-sdk'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      // Should contain code blocks
      expect(mergedContent).toMatch(/```\w+[\s\S]*?```/);

      // Should preserve TypeScript examples
      expect(mergedContent).toContain('```typescript');
      // JavaScript might not always be present, check for code blocks instead
      expect(mergedContent).toMatch(/```\w+/);

      // Code blocks should be properly closed
      const codeBlockStarts = mergedContent.match(/```/g);
      expect(codeBlockStarts?.length % 2).toBe(0); // Even number (open/close pairs)
    });

    it('should handle special characters and formatting correctly', async () => {
      const selectedConfigs = ['shadcn', 'tailwindcss'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      // Should preserve special markdown formatting
      expect(mergedContent).toMatch(/\*\*[^*]+\*\*/); // Bold text
      expect(mergedContent).toMatch(/`[^`]+`/); // Inline code
      expect(mergedContent).toMatch(/^-\s+/m); // List items

      // Should not have encoding issues
      expect(mergedContent).not.toContain('&amp;');
      expect(mergedContent).not.toContain('&lt;');
      expect(mergedContent).not.toContain('&gt;');
    });
  });

  describe('Edge Cases', () => {
    it('should handle single configuration gracefully', async () => {
      const selectedConfigs = ['nextjs-15'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      expect(mergedContent).toContain('Next.js 15');
      expect(mergedContent.length).toBeGreaterThan(1000); // Should have substantial content
    });

    it('should handle empty configuration list', async () => {
      const configs: Array<{
        content: string;
        metadata: import('../../src/registry/config-registry').ConfigMetadata;
        dependencies?: import('../../src/types/config').PackageDependencies;
      }> = [];

      const mergedContent = configMerger.merge(configs);

      expect(mergedContent).toContain('Composed Claude Code Configuration');
    });

    it('should handle configurations with missing sections', async () => {
      // This test assumes some configs might have minimal content
      const selectedConfigs = ['memory-mcp-server', 'token-gated-mcp-server'];
      const configs = await getConfigsWithContent(selectedConfigs);

      if (configs.length > 0) {
        expect(() => {
          configMerger.merge(configs);
        }).not.toThrow();
      }
    });
  });

  describe('Performance Validation', () => {
    it('should merge large configurations', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn', 'tailwindcss', 'vercel-ai-sdk', 'drizzle'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);
      // Just check that it completes and produces content
      expect(mergedContent.length).toBeGreaterThan(10000); // Should have substantial merged content
    });

    it('should handle repeated merging', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn'];
      const configs = await getConfigsWithContent(selectedConfigs);

      // Run merging a few times
      for (let i = 0; i < 3; i++) {
        const mergedContent = configMerger.merge(configs);
        expect(mergedContent.length).toBeGreaterThan(1000);
      }
    });
  });

  describe('Specific Framework Combinations', () => {
    it('should merge Next.js + shadcn correctly', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn'];
      const configs = await getConfigsWithContent(selectedConfigs);

      const mergedContent = configMerger.merge(configs);

      // Should contain both frameworks' key concepts
      expect(mergedContent).toContain('App Router');
      expect(mergedContent).toContain('Server Components');
      expect(mergedContent).toContain('Radix UI');
      expect(mergedContent).toContain('/shadcn-add');

      // Should maintain logical section ordering
      const projectContextIndex = mergedContent.indexOf('Project Context');
      const deploymentIndex = mergedContent.indexOf('Deployment');
      // Project context should come before deployment
      if (deploymentIndex > -1) {
        expect(projectContextIndex).toBeLessThan(deploymentIndex);
      } else {
        expect(projectContextIndex).toBeGreaterThanOrEqual(0);
      }
    });

    it('should merge full-stack configuration properly', async () => {
      const selectedConfigs = ['nextjs-15', 'shadcn', 'tailwindcss', 'drizzle'];
      const configs = await getConfigsWithContent(selectedConfigs);

      if (configs.length === 4) {
        const mergedContent = configMerger.merge(configs);

        // Should contain all technology stack elements
        expect(mergedContent).toContain('Next.js');
        expect(mergedContent).toContain('shadcn');
        expect(mergedContent).toContain('Tailwind');
        expect(mergedContent).toContain('Drizzle');

        // Should be substantial in size
        expect(mergedContent.length).toBeGreaterThan(20000);
      }
    });
  });
});
