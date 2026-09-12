const fs = require('fs');
const os = require('os');
const path = require('path');

function getStandardInstallTargets(cwd = process.cwd()) {
  const homeDir = process.env.HOME || os.homedir();
  return [
    {
      scope: 'global',
      label: 'global',
      path: path.join(homeDir, '.claude', 'skills'),
    },
    {
      scope: 'project',
      label: 'project',
      path: path.join(cwd, '.agents', 'skills'),
    },
  ];
}

function listInstalledSkillNamesInDir(dirPath) {
  if (!dirPath || !fs.existsSync(dirPath)) return [];

  try {
    return fs.readdirSync(dirPath).filter((name) => {
      const skillPath = path.join(dirPath, name);
      return fs.statSync(skillPath).isDirectory()
        && fs.existsSync(path.join(skillPath, 'SKILL.md'));
    });
  } catch {
    return [];
  }
}

function buildInstallStateIndex(options = {}) {
  const cwd = options.cwd || process.cwd();
  const targets = getStandardInstallTargets(cwd).map((target) => ({
    ...target,
    names: listInstalledSkillNamesInDir(target.path),
  }));

  const bySkill = new Map();

  for (const target of targets) {
    for (const name of target.names) {
      if (!bySkill.has(name)) {
        bySkill.set(name, {
          global: false,
          project: false,
        });
      }
      bySkill.get(name)[target.scope] = true;
    }
  }

  return {
    cwd,
    targets,
    bySkill,
  };
}

function getInstallState(index, skillName) {
  const empty = {
    global: false,
    project: false,
    installed: false,
    label: null,
  };

  if (!index || !skillName) return empty;

  const state = index.bySkill.get(skillName);
  if (!state) return empty;

  const label = state.global && state.project
    ? 'installed globally + project'
    : state.global
      ? 'installed globally'
      : state.project
        ? 'installed in project'
        : null;

  return {
    global: Boolean(state.global),
    project: Boolean(state.project),
    installed: Boolean(state.global || state.project),
    label,
  };
}

function formatInstallStateLabel(state) {
  return state?.label || null;
}

function getInstalledSkillNames(index, scope = null) {
  if (!index) return [];

  if (!scope) {
    return [...index.bySkill.keys()].sort();
  }

  const target = index.targets.find((entry) => entry.scope === scope);
  return target ? [...target.names].sort() : [];
}

module.exports = {
  buildInstallStateIndex,
  formatInstallStateLabel,
  getInstallState,
  getInstalledSkillNames,
  getStandardInstallTargets,
  listInstalledSkillNamesInDir,
};
