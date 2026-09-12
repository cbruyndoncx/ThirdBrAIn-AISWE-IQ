export const content = `
1. **Documentation must be verified by code**: Never trust documentation; always validate it
2. **Fail fast**: If docs are out of sync, CI should fail immediately
3. **Self-hosting**: Codumentation uses itself to validate its own documentation
4. **Explicit is better than implicit**: Each claim in docs should have a corresponding validation
5. **Logging for improvement**: Track which validations fail frequently to identify brittleness
`;

export const validate = async () => {
  // This is mostly philosophical, but we can verify the project uses itself
  const fs = require('fs');
  const path = require('path');

  // Check that README.md.codx exists (self-hosting)
  const readmeCodx = path.join(__dirname, '..', 'README.md.codx');
  if (!fs.existsSync(readmeCodx)) {
    throw new Error('Project claims to be self-hosting but README.md.codx does not exist');
  }
};

export const errorContent = `
[Validation Failed] Key principles claim self-hosting but evidence not found.
Ensure the project actually uses codumentation on itself.
`;
