import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';

export const content = `## How It Works

### File Structure

For each markdown file (e.g., \`README.md\`), create a \`.codx\` folder:

\`\`\`
README.md           # The generated output
README.md.codx/     # The source of truth
  index.md          # Template with placeholders (double braces around names)
  intro.ts          # Module for intro section
  features.ts       # Module for features section
  _meta.ts          # Meta-validator (checks adoption)
\`\`\`

### Module Interface

Each \`.ts\` module exports three things:

\`\`\`typescript
// content: The text to inject into the template
export const content = \\\`## Features
- Fast validation
- TypeScript support\\\`;

// validate: Async function that throws if claims are false
export const validate = async () => {
  if (!fs.existsSync('src/validator.ts')) {
    throw new Error('Claims validation but validator.ts missing');
  }
};

// errorContent: Human-readable explanation when validation fails
export const errorContent = \\\`
Features section claims validation support but validator is missing.
Run: touch src/validator.ts
\\\`;
\`\`\`

### Template Rendering

The \`index.md\` template uses double-brace placeholders like \`{​{ name }​}\` (where \`name\` maps to \`name.ts\`):

\`\`\`markdown
# My Project

{​{ intro }​}

{​{ features }​}

{​{ license }​}
\`\`\`

Each placeholder maps to a \`.ts\` module with the same name.`;

export const validate = async () => {
  const srcDir = path.join(__dirname, '..');

  // Verify the CodxModule interface exists in types
  const typesPath = path.join(srcDir, 'src', 'types.ts');
  const typesContent = fs.readFileSync(typesPath, 'utf-8');

  const requiredExports = ['content', 'validate', 'errorContent'];
  for (const exp of requiredExports) {
    if (!typesContent.includes(exp)) {
      throw new Error(`CodxModule interface should define '${exp}' property`);
    }
  }

  // Verify we actually have a README.md.codx with the structure shown
  const readmeCodx = path.join(srcDir, 'README.md.codx');
  if (!fs.existsSync(readmeCodx)) {
    throw new Error('Example shows README.md.codx but it does not exist');
  }

  const indexMd = path.join(readmeCodx, 'index.md');
  if (!fs.existsSync(indexMd)) {
    throw new Error('Example shows index.md in .codx but it does not exist');
  }

  // Verify template uses {{ placeholder }} syntax
  const templateContent = fs.readFileSync(indexMd, 'utf-8');
  if (!/\{\{\s*\w+\s*\}\}/.test(templateContent)) {
    throw new Error('Template should use {{ placeholder }} syntax');
  }
};

export const errorContent = `
[How It Works Validation Failed]

The section explains the module interface and file structure,
but the actual implementation doesn't match.

Ensure:
- types.ts defines CodxModule with content, validate, errorContent
- README.md.codx/ exists with index.md template
- Template uses double-brace placeholder syntax
`;
