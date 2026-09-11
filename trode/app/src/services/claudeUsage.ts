export interface UsageStats {
  fiveHourWindow: { percentage: number; resetsIn: string };
  weekly: { percentage: number; resetsAt: string };
  today: { messages: number; tokens: number; estimatedCost: number };
}

export function getUsageStats(): UsageStats {
  // Mock data for now - real implementation will parse ~/.claude/
  return {
    fiveHourWindow: { percentage: 20, resetsIn: '4h 54m' },
    weekly: { percentage: 51, resetsAt: 'Mon 2:59 PM' },
    today: { messages: 6, tokens: 753200, estimatedCost: 2.47 },
  };
}

export function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(1)}M`;
  }
  if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}K`;
  }
  return tokens.toString();
}

export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}
