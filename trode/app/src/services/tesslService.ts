const API_BASE = 'https://api.tessl.io';
const REQUEST_TIMEOUT = 10000;

export interface SkillEval {
  skillName: string;
  reviewScore: number | null;
  evalImprovement: number | null;
  hasEval: boolean;
  source: string | null;
}

// Known skill data from tessl.io (fallback when API unavailable)
interface KnownSkillData {
  reviewScore: number;
  evalImprovement: number;
}

const KNOWN_SKILL_DATA: Record<string, KnownSkillData> = {
  'frontend-design': { reviewScore: 90, evalImprovement: 24.6 },
  'karpathy-guidelines': { reviewScore: 88, evalImprovement: -3.5 }, // NEGATIVE - key marketing hook!
  'remotion-best-practices': { reviewScore: 100, evalImprovement: 25.5 },
  'remotion': { reviewScore: 100, evalImprovement: 25.5 },
  'vercel-react-best-practices': { reviewScore: 78, evalImprovement: 16.5 },
  'agent-browser': { reviewScore: 71, evalImprovement: 42.5 },
  'expo-guidelines': { reviewScore: 82, evalImprovement: 10.0 },
  'react-native-skills': { reviewScore: 75, evalImprovement: 8.0 },
};

// Known skill GitHub paths for Skills API
interface SkillGitHubInfo {
  provider: 'github';
  owner: string;
  repo: string;
  skillPath: string;
}

const KNOWN_SKILL_PATHS: Record<string, SkillGitHubInfo> = {
  'frontend-design': {
    provider: 'github',
    owner: 'anthropics',
    repo: 'skills',
    skillPath: 'frontend-design',
  },
  'karpathy-guidelines': {
    provider: 'github',
    owner: 'forrestchang',
    repo: 'andrej-karpathy-skills',
    skillPath: 'karpathy-guidelines',
  },
  'vercel-react-best-practices': {
    provider: 'github',
    owner: 'vercel-labs',
    repo: 'agent-skills',
    skillPath: 'vercel-react-best-practices',
  },
  'remotion-best-practices': {
    provider: 'github',
    owner: 'remotion-dev',
    repo: 'skills',
    skillPath: 'remotion',
  },
  'remotion': {
    provider: 'github',
    owner: 'remotion-dev',
    repo: 'skills',
    skillPath: 'remotion',
  },
};

// Cache to avoid repeated lookups
const evalCache: Map<string, SkillEval> = new Map();

// Type definitions for API responses
interface TileVersionData {
  evalScore: number | null;
  evalBaselineScore: number | null;
  evalImprovement: number | null;
  evalImprovementMultiplier: number | null;
}

interface TileData {
  attributes: {
    name: string;
    fullName: string;
    versions?: TileVersionData[];
  };
}

interface TilesApiResponse {
  data: TileData[];
  meta?: { count: number };
}

interface SkillApiResponse {
  data: {
    attributes: {
      name: string;
      reviewScore: number | null;
      sourceUrl?: string;
    };
  };
}

/**
 * Fetch tile data from Tessl Tiles API
 * Uses filter[fullName][like] to search by skill name
 */
async function fetchTileData(skillName: string): Promise<{
  evalImprovement: number | null;
  fullName: string | null;
} | null> {
  try {
    const url = `${API_BASE}/v1/tiles?filter[fullName][like]=${encodeURIComponent(skillName)}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal: AbortSignal.timeout(REQUEST_TIMEOUT),
    });

    if (!response.ok) {
      console.log(`Tiles API returned ${response.status} for ${skillName}`);
      return null;
    }

    const data: TilesApiResponse = await response.json();

    if (data.data && data.data.length > 0) {
      // Find best match - prefer exact name match
      const match =
        data.data.find(
          (tile) =>
            tile.attributes.name === skillName ||
            tile.attributes.fullName.includes(skillName)
        ) || data.data[0];

      // Get latest version's eval data
      const versions = match.attributes.versions;
      if (versions && versions.length > 0) {
        const latestVersion = versions[0];
        return {
          evalImprovement: latestVersion.evalImprovement,
          fullName: match.attributes.fullName,
        };
      }
    }

    return null;
  } catch (error) {
    console.log(`Tiles API error for ${skillName}:`, error);
    return null;
  }
}

/**
 * Fetch skill review data from Tessl Skills API
 * Requires knowing the GitHub path: provider/owner/repo/skillName
 */
async function fetchSkillReview(
  provider: string,
  owner: string,
  repo: string,
  skillName: string
): Promise<{ reviewScore: number | null; sourceUrl: string | null } | null> {
  try {
    const url = `${API_BASE}/experimental/skills/${provider}/${owner}/${repo}/${skillName}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal: AbortSignal.timeout(REQUEST_TIMEOUT),
    });

    if (!response.ok) {
      console.log(`Skills API returned ${response.status} for ${skillName}`);
      return null;
    }

    const data: SkillApiResponse = await response.json();

    return {
      reviewScore: data.data.attributes.reviewScore,
      sourceUrl: data.data.attributes.sourceUrl || null,
    };
  } catch (error) {
    console.log(`Skills API error for ${skillName}:`, error);
    return null;
  }
}

/**
 * Fetch evaluation data for a skill
 * Strategy: Tiles API → Skills API → Fallback
 */
export async function fetchSkillEval(skillName: string): Promise<SkillEval> {
  // Check cache first
  if (evalCache.has(skillName)) {
    return evalCache.get(skillName)!;
  }

  let reviewScore: number | null = null;
  let evalImprovement: number | null = null;
  let source: string | null = null;
  let hasEval = false;

  // Strategy 1: Try Tiles API for evalImprovement (most important metric)
  const tileData = await fetchTileData(skillName);
  if (tileData) {
    evalImprovement = tileData.evalImprovement;
    if (evalImprovement !== null) {
      hasEval = true;
      source = tileData.fullName
        ? `https://tessl.io/registry/${tileData.fullName}`
        : null;
    }
  }

  // Strategy 2: Try Skills API for reviewScore (if we know the GitHub path)
  const skillPath = KNOWN_SKILL_PATHS[skillName];
  if (skillPath) {
    const skillData = await fetchSkillReview(
      skillPath.provider,
      skillPath.owner,
      skillPath.repo,
      skillPath.skillPath
    );
    if (skillData) {
      reviewScore = skillData.reviewScore;
      source = source || skillData.sourceUrl;
      hasEval = hasEval || reviewScore !== null;
    }
  }

  // Strategy 3: Fall back to hardcoded data if API calls failed
  if (!hasEval) {
    const known = KNOWN_SKILL_DATA[skillName];
    if (known) {
      reviewScore = known.reviewScore;
      evalImprovement = known.evalImprovement;
      hasEval = true;
      source = `https://tessl.io/registry?q=${encodeURIComponent(skillName)}`;
    }
  }

  const evalResult: SkillEval = {
    skillName,
    reviewScore,
    evalImprovement,
    hasEval,
    source,
  };

  evalCache.set(skillName, evalResult);
  return evalResult;
}

/**
 * Fetch evaluations for multiple skills in parallel
 */
export async function fetchSkillEvals(
  skillNames: string[]
): Promise<Map<string, SkillEval>> {
  const results = new Map<string, SkillEval>();

  // Fetch all in parallel
  const evals = await Promise.all(
    skillNames.map((name) => fetchSkillEval(name))
  );

  evals.forEach((evalResult) => {
    results.set(evalResult.skillName, evalResult);
  });

  return results;
}

/**
 * Clear the eval cache (useful for refresh)
 */
export function clearEvalCache(): void {
  evalCache.clear();
}
