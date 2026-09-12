#!/usr/bin/env node

const path = require('path');
const { spawnSync } = require('child_process');

const cliPath = path.join(__dirname, '..', 'cli.js');
const args = process.argv.slice(2);
const hasExplicitFormat = args.includes('--format');
const result = spawnSync(process.execPath, [cliPath, 'vendor', ...args, ...(hasExplicitFormat ? [] : ['--format', 'text'])], {
  stdio: 'inherit',
});

if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}

process.exit(result.status === null ? 1 : result.status);
