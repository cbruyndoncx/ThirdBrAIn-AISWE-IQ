const fs = require('fs');
const path = require('path');

const { ROOT_DIR } = require('./paths.cjs');

const WORKSPACE_DIR_NAME = '.ai-agent-skills';
const WORKSPACE_CONFIG_NAME = 'config.json';

function createLibraryContext(rootDir, mode = 'bundled') {
  const resolvedRoot = path.resolve(rootDir);
  const isWorkspace = mode === 'workspace';

  return {
    mode,
    rootDir: resolvedRoot,
    skillsDir: path.join(resolvedRoot, 'skills'),
    skillsJsonPath: path.join(resolvedRoot, 'skills.json'),
    readmePath: path.join(resolvedRoot, 'README.md'),
    workAreasPath: path.join(resolvedRoot, 'WORK_AREAS.md'),
    workspaceDir: path.join(resolvedRoot, WORKSPACE_DIR_NAME),
    workspaceConfigPath: isWorkspace
      ? path.join(resolvedRoot, WORKSPACE_DIR_NAME, WORKSPACE_CONFIG_NAME)
      : null,
  };
}

const BUNDLED_LIBRARY_CONTEXT = createLibraryContext(ROOT_DIR, 'bundled');

function getBundledLibraryContext() {
  return { ...BUNDLED_LIBRARY_CONTEXT };
}

function isManagedWorkspaceRoot(rootDir) {
  if (!rootDir) return false;

  const resolvedRoot = path.resolve(rootDir);
  return fs.existsSync(path.join(resolvedRoot, 'skills.json'))
    && fs.existsSync(path.join(resolvedRoot, WORKSPACE_DIR_NAME, WORKSPACE_CONFIG_NAME));
}

function resolveLibraryContext(startDir = process.cwd()) {
  let current = path.resolve(startDir);

  while (true) {
    if (isManagedWorkspaceRoot(current)) {
      return createLibraryContext(current, 'workspace');
    }

    const parent = path.dirname(current);
    if (parent === current) {
      return getBundledLibraryContext();
    }
    current = parent;
  }
}

function readWorkspaceConfig(context) {
  if (!context || context.mode !== 'workspace' || !context.workspaceConfigPath) {
    return null;
  }

  try {
    return JSON.parse(fs.readFileSync(context.workspaceConfigPath, 'utf8'));
  } catch {
    return null;
  }
}

module.exports = {
  WORKSPACE_CONFIG_NAME,
  WORKSPACE_DIR_NAME,
  createLibraryContext,
  getBundledLibraryContext,
  isManagedWorkspaceRoot,
  readWorkspaceConfig,
  resolveLibraryContext,
};
