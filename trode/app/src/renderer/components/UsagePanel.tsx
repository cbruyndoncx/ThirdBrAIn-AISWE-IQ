import { ProgressBar } from './ProgressBar';
import { UsageStats, formatTokens, formatCost } from '../../services/claudeUsage';

interface UsagePanelProps {
  stats: UsageStats;
}

export function UsagePanel({ stats }: UsagePanelProps) {
  return (
    <div className="usage-panel">
      {/* 5-Hour Window */}
      <div className="usage-section">
        <div className="usage-header">
          <span className="usage-label">5-Hour Window</span>
          <span className="usage-value mono">{stats.fiveHourWindow.percentage}%</span>
        </div>
        <ProgressBar percentage={stats.fiveHourWindow.percentage} />
        <div className="usage-subtitle">Resets in {stats.fiveHourWindow.resetsIn}</div>
      </div>

      {/* Weekly Limit */}
      <div className="usage-section">
        <div className="usage-header">
          <span className="usage-label">Weekly</span>
          <span className="usage-value mono">{stats.weekly.percentage}%</span>
        </div>
        <ProgressBar percentage={stats.weekly.percentage} />
        <div className="usage-subtitle">Resets {stats.weekly.resetsAt}</div>
      </div>

      {/* Today's Stats */}
      <div className="usage-section today-section">
        <div className="usage-header">
          <span className="usage-label">Today</span>
        </div>
        <div className="today-stats">
          <div className="stat-row">
            <span className="stat-label">Messages:</span>
            <span className="stat-value mono">{stats.today.messages}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Tokens:</span>
            <span className="stat-value mono">{formatTokens(stats.today.tokens)}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Est. Cost:</span>
            <span className="stat-value mono">{formatCost(stats.today.estimatedCost)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
