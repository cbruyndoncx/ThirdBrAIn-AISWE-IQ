import yaml from 'js-yaml';
import type { Agent, Command, Hook, Settings } from '../parser/config-parser';
import type { HookCommand, HookEntry, HooksConfig, StatusLine } from '../types/config';

/**
 * Handles the intelligent merging of configuration components from multiple sources
 *
 * This class provides sophisticated merging logic for:
 * - AI agents with tool combination and conflict resolution
 * - Commands with override and deduplication strategies
 * - Hooks with script combination and execution order
 * - Settings with deep merging and permission handling
 *
 * @example
 * ```typescript
 * const merger = new ComponentMerger();
 *
 * // Merge agents from multiple configurations
 * const agents = merger.mergeAgents([
 *   nextjsAgents,
 *   shadcnAgents,
 *   customAgents
 * ]);
 *
 * // Generate final agent files
 * agents.forEach(agent => {
 *   const content = merger.generateAgentFile(agent);
 *   fs.writeFileSync(`agents/${agent.name}.md`, content);
 * });
 * ```
 */
export class ComponentMerger {
  /**
   * Merges agent configurations from multiple sources with intelligent deduplication
   *
   * Agents with similar names are merged by combining their tools and content.
   * Later configurations take precedence for metadata like descriptions.
   *
   * @param agentGroups - Array of agent arrays from different configurations
   * @returns Merged and deduplicated array of agents
   *
   * @example
   * ```typescript
   * const merger = new ComponentMerger();
   * const merged = merger.mergeAgents([
   *   [{ name: 'nextjs-expert', tools: ['fs'], content: '...' }],
   *   [{ name: 'nextjs-expert', tools: ['web'], content: '...' }]
   * ]);
   * // Result: Single agent with tools: ['fs', 'web']
   * ```
   */
  mergeAgents(agentGroups: Agent[][]): Agent[] {
    const mergedAgents = new Map<string, Agent>();

    for (const agents of agentGroups) {
      for (const agent of agents) {
        const key = this.normalizeKey(agent.name);

        if (!mergedAgents.has(key)) {
          mergedAgents.set(key, agent);
        } else {
          // Merge similar agents by combining their content
          const existing = mergedAgents.get(key);
          if (!existing) continue;
          const merged = this.mergeAgent(existing, agent);
          mergedAgents.set(key, merged);
        }
      }
    }

    return Array.from(mergedAgents.values());
  }

  private mergeAgent(agent1: Agent, agent2: Agent): Agent {
    // Combine tools from both agents
    const tools = new Set([...(agent1.tools || []), ...(agent2.tools || [])]);

    // Combine content with source attribution
    const content = [
      `# ${agent1.name}`,
      '',
      agent2.description || agent1.description,
      '',
      '## Combined expertise from multiple configurations',
      '',
      `### From ${agent1.source}:`,
      agent1.content,
      '',
      `### From ${agent2.source}:`,
      agent2.content,
    ].join('\n');

    return {
      name: agent1.name,
      description: agent2.description || agent1.description, // Prefer newer description
      tools: Array.from(tools),
      content,
      source: `${agent1.source} + ${agent2.source}`,
    };
  }

  mergeCommands(commandGroups: Command[][]): Command[] {
    const mergedCommands = new Map<string, Command>();

    for (const commands of commandGroups) {
      for (const command of commands) {
        const key = this.normalizeKey(command.name);

        // Always use the latest command to override previous ones
        mergedCommands.set(key, command);
      }
    }

    return Array.from(mergedCommands.values());
  }

  mergeHooks(hookGroups: Hook[][]): Hook[] {
    const mergedHooks = new Map<string, Hook>();

    for (const hooks of hookGroups) {
      for (const hook of hooks) {
        const key = hook.name;

        if (!mergedHooks.has(key)) {
          mergedHooks.set(key, hook);
        } else {
          // For duplicate hooks, use the latest one
          mergedHooks.set(key, hook);
        }
      }
    }

    return Array.from(mergedHooks.values());
  }

  mergeSettings(settingsArray: (Settings | null)[]): Settings {
    const merged: Settings = {
      permissions: {
        allow: [],
        deny: [],
      },
    };

    for (const settings of settingsArray) {
      if (!settings) continue;

      // Handle permissions structure (Next.js 15 style)
      if (settings.permissions) {
        if (settings.permissions.allow) {
          if (merged.permissions) {
            merged.permissions.allow = [
              ...(merged.permissions.allow || []),
              ...settings.permissions.allow,
            ];
          }
        }
        if (settings.permissions.deny) {
          if (merged.permissions) {
            merged.permissions.deny = [
              ...(merged.permissions.deny || []),
              ...settings.permissions.deny,
            ];
          }
        }
      }

      // Also handle legacy allow/deny at root level
      if (settings.allow) {
        if (merged.permissions) {
          merged.permissions.allow = [...(merged.permissions.allow || []), ...settings.allow];
        }
      }
      if (settings.deny) {
        if (merged.permissions) {
          merged.permissions.deny = [...(merged.permissions.deny || []), ...settings.deny];
        }
      }

      // Merge environment variables
      if (settings.env) {
        merged.env = { ...(merged.env || {}), ...settings.env };
      }

      // Merge hooks (complex merge)
      if (settings.hooks) {
        merged.hooks = this.mergeHooksConfig(merged.hooks || {}, settings.hooks);
      }

      // Merge status line
      if (settings.statusLine) {
        merged.statusLine = this.mergeStatusLine(merged.statusLine, settings.statusLine);
      }

      // Merge other properties
      const otherProps = [
        'codeRules',
        'componentPatterns',
        'importOrder',
        'testingFramework',
        'buildTools',
      ];
      for (const prop of otherProps) {
        if (settings[prop]) {
          const currentValue = (merged[prop] as Record<string, unknown>) || {};
          merged[prop] = this.deepMerge(currentValue, settings[prop] as Record<string, unknown>);
        }
      }
    }

    // Deduplicate arrays in permissions
    if (merged.permissions) {
      if (merged.permissions.allow) {
        merged.permissions.allow = [...new Set(merged.permissions.allow)];
      }
      if (merged.permissions.deny) {
        merged.permissions.deny = [...new Set(merged.permissions.deny)];
      }
    }

    // Also deduplicate legacy arrays if they exist
    if (merged.allow) {
      merged.allow = [...new Set(merged.allow)];
    }
    if (merged.deny) {
      merged.deny = [...new Set(merged.deny)];
    }

    return merged;
  }

  private mergeHooksConfig(hooks1: HooksConfig, hooks2: HooksConfig): HooksConfig {
    const merged: HooksConfig = {};

    // All hook types that might appear in configurations
    const hookTypes = [
      'PreToolUse',
      'PostToolUse',
      'Stop',
      'UserPromptSubmit',
      'Notification',
      'SubagentStop',
      'SessionEnd',
      'SessionStart',
      'PreCompact',
    ];

    for (const type of hookTypes) {
      const entries1 = hooks1[type] || [];
      const entries2 = hooks2[type] || [];

      if (entries1.length > 0 || entries2.length > 0) {
        const mergedEntries: HookEntry[] = [];

        // Process entries from hooks1
        for (const entry of entries1) {
          if (this.isValidHookEntry(entry)) {
            mergedEntries.push(this.normalizeHookEntry(entry));
          }
        }

        // Process entries from hooks2
        for (const entry of entries2) {
          if (this.isValidHookEntry(entry)) {
            mergedEntries.push(this.normalizeHookEntry(entry));
          }
        }

        if (mergedEntries.length > 0) {
          merged[type] = mergedEntries;
        }
      }
    }

    return merged;
  }

  private isValidHookEntry(entry: unknown): boolean {
    return (
      entry !== null &&
      typeof entry === 'object' &&
      'hooks' in entry &&
      Array.isArray((entry as { hooks: unknown }).hooks)
    );
  }

  private normalizeHookEntry(entry: unknown): HookEntry {
    const normalized: HookEntry = {
      hooks: [],
    };

    const entryObj = entry as Record<string, unknown>;

    // Only include matcher if it exists and is not empty
    if (entryObj.matcher && entryObj.matcher !== '') {
      normalized.matcher = entryObj.matcher as string;
    }

    // Process hooks array
    if (Array.isArray(entryObj.hooks)) {
      for (const hook of entryObj.hooks) {
        if (hook && typeof hook === 'object' && 'command' in hook) {
          const hookObj = hook as Record<string, unknown>;
          const hookCommand: HookCommand = {
            type: 'command',
            command: hookObj.command as string,
          };
          if (hookObj.timeout) {
            hookCommand.timeout = hookObj.timeout as number;
          }
          normalized.hooks.push(hookCommand);
        }
      }
    }

    return normalized;
  }

  private mergeStatusLine(
    status1: StatusLine | undefined,
    status2: StatusLine | undefined
  ): StatusLine | undefined {
    if (!status1) return status2;
    if (!status2) return status1;

    // For statusLine, the later one wins completely as it's a command string
    // We can't meaningfully merge two different status line commands
    return status2;
  }

  private deepMerge(
    obj1: Record<string, unknown>,
    obj2: Record<string, unknown>
  ): Record<string, unknown> {
    // Handle arrays separately - return as-is since they're not Record types
    if (Array.isArray(obj1) && Array.isArray(obj2)) {
      return [...obj1, ...obj2] as unknown as Record<string, unknown>;
    }

    if (
      typeof obj1 === 'object' &&
      typeof obj2 === 'object' &&
      obj1 !== null &&
      obj2 !== null &&
      !Array.isArray(obj1) &&
      !Array.isArray(obj2)
    ) {
      const merged: Record<string, unknown> = { ...obj1 };

      for (const key in obj2) {
        if (key in merged && typeof merged[key] === 'object' && typeof obj2[key] === 'object') {
          merged[key] = this.deepMerge(
            merged[key] as Record<string, unknown>,
            obj2[key] as Record<string, unknown>
          );
        } else {
          merged[key] = obj2[key];
        }
      }

      return merged;
    }

    return obj2;
  }

  private normalizeKey(name: string): string {
    return name.toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  generateAgentFile(agent: Agent): string {
    const frontmatter = {
      name: agent.name,
      description: agent.description,
      tools: agent.tools,
    };

    return ['---', yaml.dump(frontmatter).trim(), '---', '', agent.content].join('\n');
  }

  generateCommandFile(command: Command): string {
    const frontmatter: Record<string, unknown> = {
      name: command.name,
      description: command.description,
    };

    if (command.allowedTools?.length) {
      frontmatter['allowed-tools'] = command.allowedTools;
    }

    if (command.argumentHint) {
      frontmatter['argument-hint'] = command.argumentHint;
    }

    return ['---', yaml.dump(frontmatter).trim(), '---', '', command.content].join('\n');
  }
}
