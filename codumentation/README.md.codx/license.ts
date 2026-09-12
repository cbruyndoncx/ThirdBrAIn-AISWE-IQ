import * as fs from 'fs';
import * as path from 'path';

export const content = `## License

MIT - see [LICENSE](./LICENSE) for details.

---

**Ready to make your documentation unbreakable?**

\`\`\`bash
npm install codumentation --save-dev
npx codumentation init README.md
\`\`\`

Happy documenting!`;

export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Verify license matches
  if (pkg.license !== 'MIT') {
    throw new Error(`README says MIT license but package.json says: ${pkg.license}`);
  }

  // Verify the init command shown actually works
  const cliPath = path.join(__dirname, '..', 'src', 'cli.ts');
  const cliContent = fs.readFileSync(cliPath, 'utf-8');

  if (!cliContent.includes("command('init")) {
    throw new Error('License section CTA mentions init command but it does not exist');
  }
};

export const errorContent = `
[License Section Validation Failed]

The license mentioned in README doesn't match package.json,
or the call-to-action command doesn't exist.

Ensure:
- package.json license matches README
- CLI has 'init' command for the CTA to work
`;
