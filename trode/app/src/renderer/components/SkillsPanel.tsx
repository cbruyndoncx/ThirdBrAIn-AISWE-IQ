import { useState, useEffect } from 'react';
import { InstalledSkill } from '../../services/skillsScanner';

interface SkillsPanelProps {
  skills: InstalledSkill[];
}

interface SkillEval {
  skillName: string;
  reviewScore: number | null;
  evalImprovement: number | null;
  hasEval: boolean;
  source: string | null;
}

// Color coding based on lift value (evalImprovement)
function getLiftClass(lift: number | null): string {
  if (lift === null) return 'no-eval';
  if (lift >= 5) return 'positive';
  if (lift >= 0) return 'neutral';
  return 'negative';
}

// Color coding based on review score percentage
function getScoreClass(score: number | null): string {
  if (score === null) return 'no-eval';
  if (score >= 80) return 'high';
  if (score >= 60) return 'mid';
  return 'low';
}

// Format lift as signed number: +24.6 or -3.5
function formatLift(lift: number | null): string {
  if (lift === null) return '—';
  const prefix = lift >= 0 ? '+' : '';
  return `${prefix}${lift.toFixed(1)}`;
}

// Format review score as percentage
function formatScore(score: number | null): string {
  if (score === null) return '';
  return `${Math.round(score)}%`;
}

export function SkillsPanel({ skills }: SkillsPanelProps) {
  const [evals, setEvals] = useState<Record<string, SkillEval>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (skills.length === 0) return;

    setLoading(true);
    const skillNames = skills.map((s) => s.name);

    window.electronAPI
      .fetchSkillEvals(skillNames)
      .then((result) => {
        setEvals(result);
      })
      .catch((err) => {
        console.error('Failed to fetch evals:', err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [skills]);

  const openTesslRegistry = () => {
    window.open('https://tessl.io/registry', '_blank');
  };

  const openSkillPage = (skillName: string) => {
    window.open(`https://tessl.io/registry?q=${encodeURIComponent(skillName)}`, '_blank');
  };

  return (
    <div className="skills-panel">
      <div className="skills-header">
        <div className="skills-title-row" title="% = skill quality | +/- = performance lift">
          <span className="skills-label">SKILLS</span>
          <span className="skills-count">{skills.length}</span>
        </div>
        {loading && <span className="skills-loading">syncing...</span>}
      </div>

      <div className="skills-grid">
        {skills.length === 0 ? (
          <div className="no-skills">No skills installed</div>
        ) : (
          skills.map((skill) => {
            const evalData = evals[skill.name];
            const score = evalData?.reviewScore ?? null;
            const lift = evalData?.evalImprovement ?? null;
            const liftClass = getLiftClass(lift);
            const scoreClass = getScoreClass(score);

            // Concise tooltip: "% = quality | +/- = performance"
            const tooltip = '% = skill quality | +/- = performance lift';

            return (
              <div
                key={skill.path}
                className={`skill-chip ${liftClass}`}
                onClick={() => openSkillPage(skill.name)}
              >
                <span className="skill-chip-name" title={tooltip}>{skill.name}</span>
                <div className="skill-chip-metrics">
                  {score !== null && (
                    <span className={`skill-chip-score ${scoreClass}`}>
                      {formatScore(score)}
                    </span>
                  )}
                  <span className={`skill-chip-lift ${liftClass}`}>
                    {formatLift(lift)}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="tessl-cta" onClick={openTesslRegistry}>
        <span className="tessl-cta-text">Get evals on tessl.io</span>
        <span className="tessl-cta-arrow">→</span>
      </div>
    </div>
  );
}
