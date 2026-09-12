import * as fs from 'fs';
import * as path from 'path';

interface Section {
  name: string;
  varName: string;
  content: string;
  heading: string;
}

/**
 * Converts a heading to a valid TypeScript variable name
 */
function toVarName(heading: string): string {
  return heading
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .split(' ')
    .map((word, i) => i === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1))
    .join('');
}

/**
 * Parses a markdown file into sections by ## headings
 */
function parseMarkdownSections(content: string): Section[] {
  const lines = content.split('\n');
  const sections: Section[] = [];

  let currentSection: Section | null = null;
  let contentLines: string[] = [];
  let beforeFirstSection: string[] = [];

  for (const line of lines) {
    const h2Match = line.match(/^## (.+)$/);

    if (h2Match) {
      // Save previous section
      if (currentSection) {
        currentSection.content = contentLines.join('\n').trim();
        sections.push(currentSection);
      } else if (contentLines.length > 0 || beforeFirstSection.length > 0) {
        // Content before first ## heading goes into "intro" section
        const introContent = [...beforeFirstSection, ...contentLines].join('\n').trim();
        if (introContent) {
          sections.push({
            name: 'intro',
            varName: 'intro',
            content: introContent,
            heading: ''
          });
        }
      }

      // Start new section
      const heading = h2Match[1];
      currentSection = {
        name: heading,
        varName: toVarName(heading),
        content: '',
        heading: `## ${heading}`
      };
      contentLines = [];
    } else {
      if (currentSection) {
        contentLines.push(line);
      } else {
        beforeFirstSection.push(line);
      }
    }
  }

  // Don't forget the last section
  if (currentSection) {
    currentSection.content = contentLines.join('\n').trim();
    sections.push(currentSection);
  } else if (beforeFirstSection.length > 0) {
    const introContent = beforeFirstSection.join('\n').trim();
    if (introContent) {
      sections.push({
        name: 'intro',
        varName: 'intro',
        content: introContent,
        heading: ''
      });
    }
  }

  // Filter out empty sections to avoid empty lines in generated files
  return sections.filter(s => s.content.trim().length > 0);
}

/**
 * Updates .gitignore to exclude codumentation log files
 */
function updateGitignore(dir: string): void {
  const gitignorePath = path.join(dir, '.gitignore');

  const entriesToAdd = [
    '# Codumentation logs',
    '.codumentation.log',
    '.codumentation-summary.log'
  ];

  let gitignoreContent = '';
  if (fs.existsSync(gitignorePath)) {
    gitignoreContent = fs.readFileSync(gitignorePath, 'utf-8');
  }

  // Check if entries already exist
  const needsUpdate = entriesToAdd.some(entry =>
    !gitignoreContent.includes(entry)
  );

  if (needsUpdate) {
    // Add entries if they don't exist
    const newEntries = entriesToAdd.filter(entry =>
      !gitignoreContent.includes(entry)
    );

    if (newEntries.length > 0) {
      // Ensure there's a newline before our section
      const separator = gitignoreContent && !gitignoreContent.endsWith('\n\n')
        ? (gitignoreContent.endsWith('\n') ? '\n' : '\n\n')
        : '';

      gitignoreContent += separator + newEntries.join('\n') + '\n';
      fs.writeFileSync(gitignorePath, gitignoreContent);
    }
  }
}

/**
 * Checks if this is an AI context file
 */
function isAIContextFile(filename: string): boolean {
  const aiContextFiles = ['CLAUDE.md', 'AGENTS.md', 'GEMINI.md', 'AI.md'];
  const upperFilename = filename.toUpperCase();
  return aiContextFiles.some(file => upperFilename === file.toUpperCase());
}

/**
 * Generates smart stub comments based on section content
 */
function generateSmartStubComments(section: Section): string[] {
  const content = section.content;
  const contentLower = content.toLowerCase();
  const suggestions: string[] = [];

  // Detect package/technology mentions
  const techPatterns: Array<{pattern: RegExp; name: string; suggestion: string}> = [
    { pattern: /next\.?js/i, name: 'Next.js', suggestion: "Verify 'next' is in package.json dependencies" },
    { pattern: /\breact\b/i, name: 'React', suggestion: "Verify 'react' is in package.json dependencies" },
    { pattern: /typescript|ts\b/i, name: 'TypeScript', suggestion: "Verify 'typescript' is in package.json devDependencies" },
    { pattern: /tailwind/i, name: 'Tailwind', suggestion: "Verify 'tailwindcss' is in package.json dependencies" },
    { pattern: /gemini/i, name: 'Gemini', suggestion: "Verify Google Gemini package (e.g., '@google/generative-ai') is in dependencies" },
    { pattern: /openai|gpt/i, name: 'OpenAI', suggestion: "Verify 'openai' is in package.json dependencies" },
    { pattern: /anthropic|claude/i, name: 'Anthropic', suggestion: "Verify '@anthropic-ai/sdk' is in package.json dependencies" },
    { pattern: /\bzod\b/i, name: 'Zod', suggestion: "Verify 'zod' is in package.json dependencies" },
    { pattern: /prisma/i, name: 'Prisma', suggestion: "Verify 'prisma' and '@prisma/client' are in dependencies" },
    { pattern: /supabase/i, name: 'Supabase', suggestion: "Verify '@supabase/supabase-js' is in dependencies" },
    { pattern: /postgres|postgresql/i, name: 'PostgreSQL', suggestion: "Verify postgres client (e.g., 'pg') is in dependencies" },
  ];

  for (const {pattern, name, suggestion} of techPatterns) {
    if (pattern.test(content)) {
      suggestions.push(suggestion);
    }
  }

  // Detect file/directory mentions (paths with / or src, lib, etc.)
  if (/\b(src|lib|components|pages|api|utils|types|models|db|database)\/|\.(ts|tsx|js|jsx|json|md)\b/i.test(content)) {
    suggestions.push('Check that mentioned file paths and directories actually exist');
  }

  // Detect environment variables
  if (/\b(api[_\s]?key|database[_\s]?url|secret|token|password|\.env|environment\s+variable)/i.test(contentLower)) {
    suggestions.push('Validate environment variables are documented in .env.example');
  }

  // Detect architectural/structural claims
  if (/\b(architecture|structure|pattern|design|organized|folder|directory)\b/i.test(contentLower)) {
    suggestions.push('Validate architectural patterns (e.g., no forbidden patterns, consistent structure)');
  }

  // Detect commands/scripts mentions
  if (/\b(npm\s+run|yarn|pnpm|bun\s+run|npm\s+start|build|test|dev|start)\b/i.test(contentLower)) {
    suggestions.push('Verify mentioned npm scripts exist in package.json');
  }

  // Detect strict mode / code quality claims
  if (/\b(strict\s+mode|no\s+any|type\s+safe|typescript\s+strict)\b/i.test(contentLower)) {
    suggestions.push('Validate TypeScript strict mode is enabled in tsconfig.json');
    suggestions.push("Check codebase doesn't contain 'any' types if claimed");
  }

  // Detect configuration files
  if (/\b(config|configuration|tsconfig|package\.json|\.env|\.eslint)\b/i.test(contentLower)) {
    suggestions.push('Verify mentioned configuration files exist and have correct settings');
  }

  // Always add creativity encouragement
  if (suggestions.length === 0) {
    suggestions.push('Read this section carefully and add specific validations for the claims made');
  }

  suggestions.push('Think creatively: what hidden rules, patterns, or standards should be validated?');

  return suggestions;
}

/**
 * Generates a module file for a section
 */
function generateModuleContent(section: Section, isAIContext: boolean = false): string {
  const escapedContent = section.content
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$/g, '\\$');

  const headingLine = section.heading ? `${section.heading}\n\n` : '';

  const aiContextNote = isAIContext ? `
  //
  // IMPORTANT: If you are an LLM/AI agent working on this codebase:
  // After making code changes, ALWAYS run: npx codumentation validate
  // This ensures your changes align with the documented architecture and rules.
  //` : '';

  // Generate smart stub comments based on section content
  const smartSuggestions = generateSmartStubComments(section);
  const suggestionLines = smartSuggestions.map(s => `  // - ${s}`).join('\n');

  return `import * as fs from 'fs';
import * as path from 'path';

export const content = \`${headingLine}${escapedContent}
\`;

export const validate = async () => {
  // TODO: Add validation for this section
  //
  // Based on this section's content, consider validating:
${suggestionLines}${aiContextNote}
  //
  // See .codumentation-guide.md for more validation patterns and examples
};

export const errorContent = \`
[Validation Failed] The "${section.name}" section validation failed.

Review this section and ensure the documentation matches the actual codebase state.
\`;
`;
}

/**
 * Generates the index.md template
 */
function generateIndexTemplate(sections: Section[]): string {
  const sectionPlaceholders = sections
    .map(s => `{{ ${s.varName} }}`)
    .join('\n\n');

  // Add _meta at the end (it has empty content but runs validation)
  return `${sectionPlaceholders}\n\n{{ _meta }}`;
}

/**
 * Generates the meta validator that checks adoption
 */
function generateMetaValidator(sections: Section[], isAIContext: boolean = false): string {
  const sectionNames = sections
    .filter(s => s.varName !== 'intro')
    .map(s => `'${s.varName}'`)
    .join(', ');

  return `import * as fs from 'fs';
import * as path from 'path';

const SECTIONS = [${sectionNames}];
const MIN_VALIDATED_RATIO = 0.5; // At least 50% of sections should have real validations

export const content = ''; // Meta validator produces no content

export const validate = async () => {
  const codxDir = __dirname;

  // Count modules with real validations (not just TODO stubs)
  let modulesWithValidation = 0;
  let totalModules = 0;

  for (const section of SECTIONS) {
    const modulePath = path.join(codxDir, \`\${section}.ts\`);
    if (!fs.existsSync(modulePath)) continue;

    totalModules++;
    const content = fs.readFileSync(modulePath, 'utf-8');

    // Check if validate function has actual logic (not just TODO comments)
    const validateMatch = content.match(/export const validate = async \\(\\) => \\{([\\s\\S]*?)\\};/);
    if (validateMatch) {
      const validateBody = validateMatch[1];
      // Has actual code beyond comments and whitespace
      const hasRealValidation = validateBody
        .split('\\n')
        .some(line => {
          const trimmed = line.trim();
          return trimmed &&
                 !trimmed.startsWith('//') &&
                 !trimmed.startsWith('*') &&
                 trimmed !== '';
        });

      if (hasRealValidation) {
        modulesWithValidation++;
      }
    }
  }

  if (totalModules === 0) {
    throw new Error('No section modules found in .codx directory');
  }

  const ratio = modulesWithValidation / totalModules;

  if (ratio < MIN_VALIDATED_RATIO) {
    const needed = Math.ceil(MIN_VALIDATED_RATIO * totalModules);
    throw new Error(
      \`Only \${modulesWithValidation}/\${totalModules} sections have real validations. \\n\` +
      \`Need at least \${needed} sections with validations (50%).\\n\\n\` +
      \`Add meaningful validate() functions to your section modules.\\n\` +
      \`See .codumentation-guide.md for example validation patterns.\`
    );
  }
};

export const errorContent = \`
[Codumentation Setup Incomplete]
${isAIContext ? `
**IMPORTANT for AI Agents**: After making any code changes to this codebase,
you MUST run \\\`npx codumentation validate\\\` to ensure your changes align with
the documented architecture and rules.

` : ''}Your documentation is not fully validated yet. To complete setup:

1. Open each section module in the .codx folder
2. Add meaningful validate() functions that verify the documentation claims
3. Run 'codumentation validate' again

See .codumentation-guide.md for example validation patterns.
\`;
`;
}

/**
 * Generates the guide file with example validation patterns
 */
function generateGuide(): string {
  return `# Codumentation Guide

This project uses **codumentation** to ensure documentation stays in sync with the codebase.

## How It Works

Each markdown file (e.g., README.md) has a corresponding \`.codx\` folder containing:
- \`index.md\` - Template with \`{{ variableName }}\` placeholders
- \`*.ts\` modules - Each exports \`content\`, \`validate()\`, and \`errorContent\`

When you run \`codumentation validate\`, it:
1. Loads each module and runs its \`validate()\` function
2. If validation passes, renders the template with module content
3. Compares rendered output to the actual markdown file

If code changes break documentation claims, validation fails and CI catches it.

## Adding Validations

The initial setup creates stub \`validate()\` functions. Replace them with real validations!

### Example: Validate Mentioned Files Exist

\`\`\`typescript
export const validate = async () => {
  const mentionedFiles = ['src/lib/worker/index.ts', 'db/agents/supergod.json'];
  for (const file of mentionedFiles) {
    if (!fs.existsSync(path.join(__dirname, '..', file))) {
      throw new Error(\`Documentation mentions \${file} but it doesn't exist\`);
    }
  }
};
\`\`\`

### Example: Validate Dependencies

\`\`\`typescript
export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  const requiredDeps = ['next', 'typescript', 'zod'];
  for (const dep of requiredDeps) {
    if (!pkg.dependencies?.[dep] && !pkg.devDependencies?.[dep]) {
      throw new Error(\`Documentation mentions \${dep} but it's not in package.json\`);
    }
  }
};
\`\`\`

### Example: Validate TypeScript Strict Mode

\`\`\`typescript
export const validate = async () => {
  const tsconfigPath = path.join(__dirname, '..', 'tsconfig.json');
  const tsconfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf-8'));

  if (!tsconfig.compilerOptions?.strict) {
    throw new Error('Documentation claims strict TypeScript but tsconfig.json has strict: false');
  }
};
\`\`\`

### Example: Validate No \`any\` Types (Code Quality)

\`\`\`typescript
import { execSync } from 'child_process';

export const validate = async () => {
  try {
    const result = execSync('grep -r ": any\\\\|as any" src/ --include="*.ts" --include="*.tsx" || true', {
      encoding: 'utf-8',
      cwd: path.join(__dirname, '..')
    });
    if (result.trim()) {
      throw new Error(\`Found 'any' types in codebase:\\n\${result}\`);
    }
  } catch (e) {
    // grep returns non-zero if no matches, which is good
  }
};
\`\`\`

### Example: Validate API Routes Have Zod Schemas

\`\`\`typescript
import { assertGlobMatches } from 'codumentation/helpers';

export const validate = async () => {
  const apiRoutes = assertGlobMatches('src/pages/api/**/*.ts', {
    cwd: path.join(__dirname, '..')
  });

  for (const route of apiRoutes) {
    const content = fs.readFileSync(path.join(__dirname, '..', route), 'utf-8');
    if (!content.includes('z.object') && !content.includes('from \\'zod\\'')) {
      throw new Error(\`API route \${route} missing Zod validation\`);
    }
  }
};
\`\`\`

### Example: Validate Environment Variables Documented

\`\`\`typescript
export const validate = async () => {
  const envExamplePath = path.join(__dirname, '..', '.env.example');
  if (!fs.existsSync(envExamplePath)) {
    throw new Error('Documentation mentions env vars but .env.example not found');
  }

  const envExample = fs.readFileSync(envExamplePath, 'utf-8');
  const documentedVars = ['GEMINI_API_KEY', 'DATABASE_URL'];

  for (const v of documentedVars) {
    if (!envExample.includes(v)) {
      throw new Error(\`Documentation mentions \${v} but .env.example doesn't have it\`);
    }
  }
};
\`\`\`

### Example: Validate Single Components Folder

\`\`\`typescript
import { assertSingleDirectory } from 'codumentation/helpers';

export const validate = async () => {
  // Throws if multiple 'components' directories exist
  assertSingleDirectory('components', {
    cwd: path.join(__dirname, '..')
  });
};
\`\`\`

## Commands

- \`codumentation validate\` - Check all documentation is valid
- \`codumentation build\` - Regenerate markdown files from modules
- \`codumentation stats\` - View validation failure statistics

## Integration with Development Workflow

### Add to package.json

\`\`\`json
{
  "scripts": {
    "codumentation:validate": "codumentation validate",
    "codumentation:build": "codumentation build"
  }
}
\`\`\`

### TypeScript Configuration

You may want to exclude \`.codx\` folders from compilation since they contain validation modules:

\`\`\`json
// tsconfig.json
{
  "exclude": ["**/*.codx/**"]
}
\`\`\`

### Pre-commit Hook

Using husky:

\`\`\`bash
npx husky add .husky/pre-commit "npm run codumentation:validate"
\`\`\`

### CI/CD Pipeline

GitHub Actions:

\`\`\`yaml
- name: Validate Documentation
  run: npx codumentation validate
\`\`\`

GitLab CI:

\`\`\`yaml
validate-docs:
  script:
    - npx codumentation validate
\`\`\`

### Test Integration

Add to your test suite to ensure docs stay valid:

\`\`\`json
{
  "scripts": {
    "test": "vitest && codumentation validate"
  }
}
\`\`\`

## Philosophy: Be Innovative with Validations

Codumentation is not just for verifying obvious claims. Use it to **encode hidden knowledge** that would otherwise live only in your team's collective memory:

### Encode Best Practices

Instead of writing "NEVER use \`any\` types" (which LLMs might ignore), write it as a validation:

\`\`\`typescript
// This ensures the rule is enforced, not just documented
export const validate = async () => {
  const result = execSync('grep -r ": any" src/ || true', { encoding: 'utf-8' });
  if (result.trim()) {
    throw new Error('Found any types - maintain type safety');
  }
};
\`\`\`

### Replace "ALWAYS DO THIS" with Validation

Instead of: "ALWAYS validate API inputs with Zod"

Write:

\`\`\`typescript
import { assertCodePattern } from 'codumentation/helpers';

export const validate = async () => {
  // Ensure all API routes include Zod validation
  assertCodePattern(
    'src/pages/api/**/*.ts',
    /z\.object|from ['"]zod['"]/,
    'All API routes must use Zod for input validation'
  );
};
\`\`\`

### For AI Agent Context Files

If you're using codumentation for CLAUDE.md, AGENTS.md, or similar:

1. **Encode unwritten rules** - Architecture decisions, coding patterns, forbidden practices
2. **Keep content focused** - Move verbose explanations into \`errorContent\`
3. **Validation guides correction** - When the LLM breaks a rule, the validation fails and \`errorContent\` teaches the fix
4. **Use stats to improve** - \`codumentation stats\` shows which rules are broken most often, guiding you to improve documentation

Example for AI context:

\`\`\`typescript
export const content = \\\`
## Code Style

We use functional React components with TypeScript strict mode.
\\\`;

export const validate = async () => {
  // Verify strict mode
  const tsconfig = JSON.parse(fs.readFileSync('tsconfig.json', 'utf-8'));
  if (!tsconfig.compilerOptions?.strict) {
    throw new Error('TypeScript strict mode must be enabled');
  }

  // Verify no class components
  const result = execSync('grep -r "class.*extends React.Component" src/ || true', { encoding: 'utf-8' });
  if (result.trim()) {
    throw new Error('Found class components - use functional components');
  }
};

export const errorContent = \\\`
[Code Style Violation]

This project uses functional React components with TypeScript strict mode.

To fix:
1. Ensure tsconfig.json has "strict": true
2. Convert any class components to functional components with hooks
3. Run \\\\\`npm run codumentation:validate\\\\\` to verify

Class components make it harder to use hooks and increase bundle size.
See: https://react.dev/reference/react/Component#alternatives
\\\`;
\`\`\`

## Tips

1. **Start with existence checks** - Verify mentioned files/dirs exist
2. **Add dependency checks** - Validate package.json has what docs claim
3. **Encode hidden rules** - Document architectural decisions as validations
4. **Be innovative** - Use validations to enforce what would otherwise be "tribal knowledge"
5. **Use errorContent wisely** - Include detailed fix instructions and reasoning
6. **Monitor stats** - Frequently failing validations indicate unclear documentation
7. **Run in CI** - Make validation part of your build pipeline
`;
}

/**
 * Initialize codumentation for a markdown file
 */
export async function initCodumentation(
  markdownPath: string,
  options: { force?: boolean } = {}
): Promise<{ codxDir: string; sections: number; guideFile: string }> {
  // Resolve paths
  const absolutePath = path.resolve(markdownPath);
  const dir = path.dirname(absolutePath);
  const filename = path.basename(absolutePath);
  const codxDir = path.join(dir, `${filename}.codx`);
  const guideFile = path.join(dir, '.codumentation-guide.md');

  // Check if markdown file exists
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`Markdown file not found: ${absolutePath}`);
  }

  // Check if .codx dir already exists
  if (fs.existsSync(codxDir) && !options.force) {
    throw new Error(
      `${filename}.codx already exists. Use --force to overwrite.`
    );
  }

  // Read and parse markdown
  const content = fs.readFileSync(absolutePath, 'utf-8');
  const sections = parseMarkdownSections(content);

  if (sections.length === 0) {
    throw new Error('No sections found in markdown file. Add some ## headings.');
  }

  // Check if this is an AI context file
  const isAIContext = isAIContextFile(filename);

  // Create .codx directory
  if (!fs.existsSync(codxDir)) {
    fs.mkdirSync(codxDir, { recursive: true });
  }

  // Generate module files for each section
  for (const section of sections) {
    const modulePath = path.join(codxDir, `${section.varName}.ts`);
    const moduleContent = generateModuleContent(section, isAIContext);
    fs.writeFileSync(modulePath, moduleContent);
  }

  // Generate index.md template
  const indexPath = path.join(codxDir, 'index.md');
  const indexContent = generateIndexTemplate(sections);
  fs.writeFileSync(indexPath, indexContent);

  // Generate meta validator
  const metaPath = path.join(codxDir, '_meta.ts');
  const metaContent = generateMetaValidator(sections, isAIContext);
  fs.writeFileSync(metaPath, metaContent);

  // Generate guide file (only if it doesn't exist)
  if (!fs.existsSync(guideFile)) {
    fs.writeFileSync(guideFile, generateGuide());
  }

  // Update .gitignore to exclude log files
  updateGitignore(dir);

  return {
    codxDir,
    sections: sections.length,
    guideFile
  };
}
