import { describe, expect, it } from 'vitest';
import { ComponentMerger } from '../src/merger/component-merger';
import { ConfigMerger } from '../src/merger/config-merger';

describe('ConfigMerger', () => {
  describe('merge', () => {
    it('should merge multiple configurations without duplicates', () => {
      const merger = new ConfigMerger();
      const configs = [
        {
          content: '# Config 1\n## Section 1\nContent 1\n## Common Section\nContent from config 1',
          metadata: {
            id: 'config1',
            name: 'Config 1',
            version: '1.0.0',
            description: 'Test config 1',
            category: 'ui' as const,
            path: '/test/config1',
            priority: 1,
          },
        },
        {
          content: '# Config 2\n## Section 2\nContent 2\n## Common Section\nContent from config 2',
          metadata: {
            id: 'config2',
            name: 'Config 2',
            version: '1.0.0',
            description: 'Test config 2',
            category: 'ui' as const,
            path: '/test/config2',
            priority: 2,
          },
        },
      ];

      const merged = merger.merge(configs);

      // Check that merged content is a string
      expect(typeof merged).toBe('string');
      expect(merged).toContain('Composed Claude Code Configuration');
      expect(merged).toContain('Config 1');
      expect(merged).toContain('Config 2');
      expect(merged).toContain('Section 1');
      expect(merged).toContain('Section 2');
    });

    it('should handle empty configurations gracefully', () => {
      const merger = new ConfigMerger();
      const configs = [];
      const merged = merger.merge(configs);

      expect(typeof merged).toBe('string');
      expect(merged).toContain('Composed Claude Code Configuration');
    });

    it('should preserve priority when merging sections', () => {
      const merger = new ConfigMerger();
      const configs = [
        {
          content: '# Low Priority\n## Content\nLow priority content',
          metadata: {
            id: 'low-priority',
            name: 'Low Priority',
            version: '1.0.0',
            description: 'Low priority config',
            category: 'ui' as const,
            path: '/test/low',
            priority: 1,
          },
        },
        {
          content: '# High Priority\n## Content\nHigh priority content',
          metadata: {
            id: 'high-priority',
            name: 'High Priority',
            version: '1.0.0',
            description: 'High priority config',
            category: 'ui' as const,
            path: '/test/high',
            priority: 10,
          },
        },
      ];

      const merged = merger.merge(configs);

      // Higher priority content should appear in merged result
      expect(merged).toContain('High priority content');
    });

    it('should merge complex nested sections', () => {
      const merger = new ConfigMerger();
      const configs = [
        {
          content:
            '# Config 1\n## Settings\nRead enabled: true\nPaths: /a\n## Development\nUse TypeScript',
          metadata: {
            id: 'config1',
            name: 'Config 1',
            version: '1.0.0',
            description: 'Config 1',
            category: 'ui' as const,
            path: '/test/config1',
            priority: 1,
          },
        },
        {
          content:
            '# Config 2\n## Settings\nRead paths: /b\nExecute enabled: true\n## Development\nUse ESLint',
          metadata: {
            id: 'config2',
            name: 'Config 2',
            version: '1.0.0',
            description: 'Config 2',
            category: 'ui' as const,
            path: '/test/config2',
            priority: 1,
          },
        },
      ];

      const merged = merger.merge(configs);

      // Check that settings from both configs are present
      expect(merged).toContain('Settings');
      expect(merged).toContain('Development');
      expect(merged).toContain('Config 1');
      expect(merged).toContain('Config 2');
    });

    it('should handle special characters in content', () => {
      const merger = new ConfigMerger();
      const configs = [
        {
          content: `# Title\n\n\`\`\`javascript\nconst x = "hello";\n\`\`\`\n\n## Special chars: \${}[]\n\nThis section has special characters like $, {}, and [] in the title.`,
          metadata: {
            id: 'special',
            name: 'Special',
            version: '1.0.0',
            description: 'Special chars test',
            category: 'ui' as const,
            path: '/test/special',
            priority: 1,
          },
        },
      ];

      const merged = merger.merge(configs);

      expect(merged).toContain('```javascript');
      expect(merged).toContain('const x = "hello"');
      // The section header "Special chars: ${}[]" should be preserved as a title
      expect(merged).toMatch(/##?\s+Special chars: \$\{\}\[\]/);
      // The content should also be preserved
      expect(merged).toContain('This section has special characters');
    });
  });
});

describe('ComponentMerger', () => {
  describe('mergeAgents', () => {
    it('should merge agents without duplicates', () => {
      const merger = new ComponentMerger();
      const agentGroups = [
        [
          {
            name: 'agent1',
            description: 'Agent 1',
            tools: ['tool1'],
            content: 'Agent 1 content',
            source: 'config1',
          },
          {
            name: 'agent2',
            description: 'Agent 2',
            tools: ['tool2'],
            content: 'Agent 2 content',
            source: 'config1',
          },
        ],
        [
          {
            name: 'agent2',
            description: 'Agent 2 updated',
            tools: ['tool2', 'tool3'],
            content: 'Agent 2 updated content',
            source: 'config2',
          },
          {
            name: 'agent3',
            description: 'Agent 3',
            tools: ['tool3'],
            content: 'Agent 3 content',
            source: 'config2',
          },
        ],
      ];

      const merged = merger.mergeAgents(agentGroups);

      expect(merged).toHaveLength(3);
      expect(merged.map(a => a.name)).toContain('agent1');
      expect(merged.map(a => a.name)).toContain('agent2');
      expect(merged.map(a => a.name)).toContain('agent3');

      // Check that agent2 has the updated description and tools
      const agent2 = merged.find(a => a.name === 'agent2');
      expect(agent2?.description).toBe('Agent 2 updated');
      expect(agent2?.tools).toContain('tool3');
    });
  });

  describe('mergeCommands', () => {
    it('should merge commands without duplicates', () => {
      const merger = new ComponentMerger();
      const commandGroups = [
        [
          {
            name: 'cmd1',
            description: 'Command 1',
            content: 'Command 1 content',
            source: 'config1',
          },
          {
            name: 'cmd2',
            description: 'Command 2',
            content: 'Command 2 content',
            source: 'config1',
          },
        ],
        [
          {
            name: 'cmd2',
            description: 'Command 2 updated',
            content: 'Command 2 updated content',
            source: 'config2',
            argumentHint: 'arg1',
          },
          {
            name: 'cmd3',
            description: 'Command 3',
            content: 'Command 3 content',
            source: 'config2',
          },
        ],
      ];

      const merged = merger.mergeCommands(commandGroups);

      expect(merged).toHaveLength(3);
      expect(merged.map(c => c.name)).toContain('cmd1');
      expect(merged.map(c => c.name)).toContain('cmd2');
      expect(merged.map(c => c.name)).toContain('cmd3');

      // Check that cmd2 has the updated description and arguments
      const cmd2 = merged.find(c => c.name === 'cmd2');
      expect(cmd2?.description).toBe('Command 2 updated');
      expect(cmd2?.argumentHint).toBe('arg1');
    });
  });

  describe('mergeHooks', () => {
    it('should merge hooks without duplicates', () => {
      const merger = new ComponentMerger();
      const hookGroups = [
        [
          {
            name: 'hook1.sh',
            content: '#!/bin/bash\necho "Hook 1"',
            type: 'script' as const,
            source: 'config1',
          },
          {
            name: 'hook2.sh',
            content: '#!/bin/bash\necho "Hook 2"',
            type: 'script' as const,
            source: 'config1',
          },
        ],
        [
          {
            name: 'hook2.sh',
            content: '#!/bin/bash\necho "Hook 2 updated"',
            type: 'script' as const,
            source: 'config2',
          },
          {
            name: 'hook3.sh',
            content: '#!/bin/bash\necho "Hook 3"',
            type: 'script' as const,
            source: 'config2',
          },
        ],
      ];

      const merged = merger.mergeHooks(hookGroups);

      expect(merged).toHaveLength(3);
      expect(merged.map(h => h.name)).toContain('hook1.sh');
      expect(merged.map(h => h.name)).toContain('hook2.sh');
      expect(merged.map(h => h.name)).toContain('hook3.sh');

      // Check that hook2 has the updated content
      const hook2 = merged.find(h => h.name === 'hook2.sh');
      expect(hook2?.content).toContain('Hook 2 updated');
    });
  });
});
