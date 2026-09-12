import * as fs from 'fs';
import * as path from 'path';

export const content = `## Optimizing AI Context Files

One of codumentation's most powerful features is using validation logs to **continuously improve AI context files** like CLAUDE.md.

### The Feedback Loop

When you use Claude Code (or similar AI agents) with a codumented CLAUDE.md:

1. **AI makes changes** based on your documented rules
2. **Validation runs** (manually or via hooks/CI)
3. **Failures are logged** to \`.codumentation-summary.log\`
4. **Stats reveal patterns** about which sections fail most
5. **You improve those sections** with better guidance
6. **Repeat** until documentation is bulletproof

\`\`\`bash
# After a long coding session with AI agents
npx codumentation stats --days 7
\`\`\`

Output might show:
\`\`\`
Validation Failure Statistics (Last 7 days)
==================================================

Total Failures: 23

Failures by Module:
  codeStyle: 12 failures ← Improve guidance!
  architecture: 7 failures ← Consider improving
  testing: 4 failures
\`\`\`

This tells you: **your code style documentation isn't clear enough** for the AI to follow consistently.

### Minimizing AI Context Files

Large CLAUDE.md files waste tokens and can confuse AI agents. Use the feedback loop to find the **minimal effective documentation**:

1. **Start with comprehensive rules**
2. **Track which validations never fail** - those rules are well understood
3. **Track which fail repeatedly** - those need better explanations
4. **Trim rules that never fail** - they might be obvious to the AI
5. **Expand rules that fail often** - add examples, clarify edge cases

### The \`errorContent\` Teaching Mechanism

When validation fails, the AI sees your \`errorContent\`. Write it as **teaching material**:

\`\`\`typescript
export const errorContent = \`
[Code Style Violation]

You used a class component, but this project uses functional components only.

WRONG:
  class MyComponent extends React.Component { ... }

RIGHT:
  function MyComponent() { ... }
  // or
  const MyComponent: React.FC = () => { ... }

Why: Functional components are smaller, easier to test, and support hooks.

See: src/components/Button.tsx for an example
\`;
\`\`\`

Now when the AI breaks this rule:
1. Validation fails immediately (not after human review)
2. AI receives specific guidance on what went wrong
3. AI learns the pattern for next time

### Practical Workflow

\`\`\`bash
# 1. After AI coding session, check what broke
npx codumentation stats

# 2. Identify problematic modules
#    Example: "architecture" fails 40% of the time

# 3. Improve that module's documentation
#    - Add more examples to content
#    - Make errorContent more instructive
#    - Add edge cases the AI missed

# 4. Re-run to verify fix
npx codumentation validate

# 5. Over time, your CLAUDE.md becomes:
#    - Smaller (remove obvious rules)
#    - More precise (clarify confusing rules)
#    - Self-correcting (errorContent teaches)
\`\`\`

### Why This Matters

Traditional AI context files are **write-once, pray-it-works**. Codumentation makes them **measurable and improvable**:

| Traditional CLAUDE.md | Codumented CLAUDE.md |
|----------------------|---------------------|
| No feedback on effectiveness | Stats show what works |
| Grows forever | Can be minimized |
| AI silently ignores unclear rules | Failures catch violations |
| Human reviews catch issues | Automated validation catches issues |
| "IMPORTANT: Never do X" | Validation prevents X |`;

export const validate = async () => {
  const srcDir = path.join(__dirname, '..');

  // Verify the stats command exists (we claim it's useful)
  const cliPath = path.join(srcDir, 'src', 'cli.ts');
  const cliContent = fs.readFileSync(cliPath, 'utf-8');

  if (!cliContent.includes("command('stats")) {
    throw new Error('AI Optimization section references stats command but it does not exist');
  }

  // Verify the --days option exists
  if (!cliContent.includes('--days')) {
    throw new Error('AI Optimization section shows --days option but it does not exist');
  }

  // Verify .codumentation-summary.log is mentioned in logger
  const loggerPath = path.join(srcDir, 'src', 'logger.ts');
  const loggerContent = fs.readFileSync(loggerPath, 'utf-8');

  if (!loggerContent.includes('codumentation-summary.log')) {
    throw new Error('AI Optimization section references summary log but logger does not create it');
  }

  // Verify we have a CLAUDE.md.codx (eating our own dog food)
  const claudeCodx = path.join(srcDir, 'CLAUDE.md.codx');
  if (!fs.existsSync(claudeCodx)) {
    throw new Error('AI Optimization section discusses CLAUDE.md but we do not have CLAUDE.md.codx');
  }
};

export const errorContent = `
[AI Optimization Section Validation Failed]

This section explains how to use logs to optimize AI context files,
but the features it references don't exist.

Ensure:
- CLI has 'stats' command with --days option
- Logger creates .codumentation-summary.log
- Project has CLAUDE.md.codx to demonstrate the concept
`;
