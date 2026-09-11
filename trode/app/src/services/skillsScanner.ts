import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface InstalledSkill {
  name: string;
  path: string;
  description?: string;
  source: 'project' | 'global';
}

export function scanForSkills(projectPath?: string): InstalledSkill[] {
  const skills: InstalledSkill[] = [];

  // Scan project-level skills
  if (projectPath) {
    const projectSkillsDir = path.join(projectPath, '.claude', 'skills');
    skills.push(...scanSkillsDirectory(projectSkillsDir, 'project'));
  }

  // Scan global skills
  const globalSkillsDir = path.join(os.homedir(), '.claude', 'skills');
  skills.push(...scanSkillsDirectory(globalSkillsDir, 'global'));

  return skills;
}

function scanSkillsDirectory(
  skillsDir: string,
  source: 'project' | 'global'
): InstalledSkill[] {
  const skills: InstalledSkill[] = [];

  if (!fs.existsSync(skillsDir)) {
    return skills;
  }

  try {
    const entries = fs.readdirSync(skillsDir, { withFileTypes: true });

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;

      const skillPath = path.join(skillsDir, entry.name);
      const skillMdPath = path.join(skillPath, 'SKILL.md');

      if (fs.existsSync(skillMdPath)) {
        const content = fs.readFileSync(skillMdPath, 'utf-8');
        const description = extractDescription(content);

        skills.push({
          name: entry.name,
          path: skillPath,
          description,
          source,
        });
      }
    }
  } catch (error) {
    console.error(`Error scanning skills directory ${skillsDir}:`, error);
  }

  return skills;
}

function extractDescription(content: string): string | undefined {
  const lines = content.split('\n');
  let inFrontmatter = false;

  for (const line of lines) {
    if (line.trim() === '---') {
      inFrontmatter = !inFrontmatter;
      continue;
    }
    if (!inFrontmatter && line.trim()) {
      // First non-empty line outside frontmatter
      // Remove markdown heading prefix and trim
      return line.replace(/^#+\s*/, '').trim().slice(0, 80);
    }
  }
  return undefined;
}

// Get project path from environment variable or return undefined
export function getProjectPath(): string | undefined {
  return process.env.SKILLS_PROJECT_PATH || undefined;
}
