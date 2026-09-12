function normalizeRequires(value) {
  if (!Array.isArray(value)) return [];

  const seen = new Set();
  const output = [];

  for (const entry of value) {
    const name = String(entry || '').trim();
    if (!name) continue;
    if (seen.has(name)) continue;
    seen.add(name);
    output.push(name);
  }

  return output;
}

function buildDependencyGraph(data) {
  const skills = Array.isArray(data?.skills) ? data.skills : [];
  const names = new Set(skills.map((skill) => skill.name));
  const requiresMap = new Map();
  const requiredByMap = new Map();
  const errors = [];

  for (const skill of skills) {
    const requires = normalizeRequires(skill.requires);
    requiresMap.set(skill.name, requires);
    requiredByMap.set(skill.name, []);

    const seen = new Set();
    for (const dependencyName of requires) {
      if (seen.has(dependencyName)) {
        errors.push(`Skill "${skill.name}" has duplicate dependency "${dependencyName}"`);
        continue;
      }
      seen.add(dependencyName);

      if (!names.has(dependencyName)) {
        errors.push(`Skill "${skill.name}" requires unknown skill "${dependencyName}"`);
      }

      if (dependencyName === skill.name) {
        errors.push(`Skill "${skill.name}" cannot require itself`);
      }
    }
  }

  for (const [skillName, requires] of requiresMap.entries()) {
    for (const dependencyName of requires) {
      if (!requiredByMap.has(dependencyName)) continue;
      requiredByMap.get(dependencyName).push(skillName);
    }
  }

  const visiting = new Set();
  const visited = new Set();

  function walk(skillName, trail = []) {
    if (visiting.has(skillName)) {
      const loopStart = trail.indexOf(skillName);
      const cycle = [...trail.slice(loopStart), skillName];
      errors.push(`Dependency cycle detected: ${cycle.join(' -> ')}`);
      return;
    }

    if (visited.has(skillName)) return;
    visiting.add(skillName);

    for (const dependencyName of requiresMap.get(skillName) || []) {
      if (!requiresMap.has(dependencyName)) continue;
      walk(dependencyName, [...trail, skillName]);
    }

    visiting.delete(skillName);
    visited.add(skillName);
  }

  for (const skill of skills) {
    walk(skill.name);
  }

  for (const [skillName, requiredBy] of requiredByMap.entries()) {
    requiredByMap.set(skillName, [...new Set(requiredBy)].sort());
  }

  return {
    requiresMap,
    requiredByMap,
    errors,
  };
}

function getSkillDependencies(data, skillName) {
  const graph = buildDependencyGraph(data);
  return graph.requiresMap.get(skillName) || [];
}

function getSkillDependents(data, skillName) {
  const graph = buildDependencyGraph(data);
  return graph.requiredByMap.get(skillName) || [];
}

function resolveInstallOrder(data, requestedSkillNames) {
  const graph = buildDependencyGraph(data);
  if (graph.errors.length > 0) {
    throw new Error(graph.errors.join('; '));
  }

  const requested = Array.isArray(requestedSkillNames) ? requestedSkillNames : [requestedSkillNames];
  const order = [];
  const seen = new Set();
  const visiting = new Set();

  function visit(skillName) {
    if (!skillName || seen.has(skillName)) return;
    if (visiting.has(skillName)) {
      throw new Error(`Dependency cycle detected while resolving install order for "${skillName}"`);
    }

    if (!graph.requiresMap.has(skillName)) {
      throw new Error(`Unknown skill "${skillName}"`);
    }

    visiting.add(skillName);
    for (const dependencyName of graph.requiresMap.get(skillName) || []) {
      visit(dependencyName);
    }
    visiting.delete(skillName);

    seen.add(skillName);
    order.push(skillName);
  }

  for (const skillName of requested) {
    visit(skillName);
  }

  return order;
}

module.exports = {
  buildDependencyGraph,
  getSkillDependencies,
  getSkillDependents,
  normalizeRequires,
  resolveInstallOrder,
};
