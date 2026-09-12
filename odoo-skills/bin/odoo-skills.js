#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");
const skillsRoot = path.join(repoRoot, "skills");

const destinations = {
  claude: path.join(os.homedir(), ".claude", "skills"),
  opencode: path.join(os.homedir(), ".config", "opencode", "skills"),
};

function usage() {
  console.log(`Odoo Skills installer

Usage:
  npx @mart337i/odoo-skills [install] [options]
  npx github:mart337i/odoo-skills [install] [options]

Options:
  --target <all|claude|opencode>  Install target. Default: all
  --dry-run                       Show what would be copied
  --help                          Show this help

Examples:
  npx @mart337i/odoo-skills
  npx @mart337i/odoo-skills --target opencode
  npx github:mart337i/odoo-skills --target claude
`);
}

function parseArgs(argv) {
  const args = [...argv];
  if (args[0] === "install") {
    args.shift();
  }

  const options = { target: "all", dryRun: false, help: false };

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === "--help" || arg === "-h") {
      options.help = true;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--target") {
      const value = args[i + 1];
      if (!value) {
        throw new Error("--target requires a value");
      }
      options.target = value;
      i += 1;
    } else if (arg.startsWith("--target=")) {
      options.target = arg.slice("--target=".length);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!["all", "claude", "opencode"].includes(options.target)) {
    throw new Error(`Invalid target: ${options.target}`);
  }

  return options;
}

function listSkills() {
  return fs
    .readdirSync(skillsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => fs.existsSync(path.join(skillsRoot, name, "SKILL.md")))
    .sort();
}

function timestamp() {
  const date = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join("");
}

function ensureDir(dir, dryRun) {
  if (dryRun) {
    console.log(`[dry-run] mkdir -p ${dir}`);
    return;
  }
  fs.mkdirSync(dir, { recursive: true });
}

function removePath(target) {
  fs.rmSync(target, { recursive: true, force: true });
}

function copySkill(source, target, backupDir, dryRun) {
  const existing = fs.lstatSync(target, { throwIfNoEntry: false });
  if (existing) {
    const backupTarget = path.join(backupDir, path.basename(target));
    if (dryRun) {
      console.log(`[dry-run] backup ${target} -> ${backupTarget}`);
    } else {
      fs.mkdirSync(backupDir, { recursive: true });
      removePath(backupTarget);
      fs.renameSync(target, backupTarget);
    }
  }

  if (dryRun) {
    console.log(`[dry-run] copy ${source} -> ${target}`);
    return;
  }

  fs.cpSync(source, target, { recursive: true, dereference: true });
}

function installTo(destName, destPath, skills, dryRun) {
  ensureDir(destPath, dryRun);
  const backupDir = path.join(destPath, `.backup-odoo-skills-${timestamp()}`);

  for (const skill of skills) {
    const source = path.join(skillsRoot, skill);
    const target = path.join(destPath, skill);
    copySkill(source, target, backupDir, dryRun);
    console.log(`${dryRun ? "would install" : "installed"} ${skill} -> ${destName}:${target}`);
  }

  if (!dryRun && fs.existsSync(backupDir) && fs.readdirSync(backupDir).length === 0) {
    fs.rmdirSync(backupDir);
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    usage();
    return;
  }

  if (!fs.existsSync(skillsRoot)) {
    throw new Error(`Cannot find skills directory: ${skillsRoot}`);
  }

  const skills = listSkills();
  if (!skills.length) {
    throw new Error(`No skills found in ${skillsRoot}`);
  }

  const targets = options.target === "all" ? Object.entries(destinations) : [[options.target, destinations[options.target]]];

  for (const [name, destPath] of targets) {
    installTo(name, destPath, skills, options.dryRun);
  }

  console.log("\nRestart or reload your agent so it picks up the installed skills.");
}

try {
  main();
} catch (error) {
  console.error(`error: ${error.message}`);
  process.exitCode = 1;
}
