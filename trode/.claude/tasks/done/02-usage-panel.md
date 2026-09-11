# Task: Claude Usage Panel UI

## Goal

Implement the Claude usage display section with mock data. Focus on UI only.

## Definition of Done

- [ ] UsagePanel component shows 5-hour window with progress bar
- [ ] UsagePanel component shows weekly limit with progress bar
- [ ] "Today" section shows messages, tokens, and estimated cost
- [ ] Progress bars have gradient fills (match Claude aesthetic)
- [ ] Numbers use monospace font
- [ ] Footer shows "Updated 0 sec ago" with refresh button (↻)
- [ ] UI matches the mockup in prompt.md
- [ ] All data comes from mock values in claudeUsage.ts

## Files to Create/Modify

```
app/src/renderer/components/
├── UsagePanel.tsx
├── ProgressBar.tsx
└── Footer.tsx

app/src/services/
└── claudeUsage.ts  (mock data for now)
```

## Mock Data to Use

```typescript
{
  fiveHourWindow: { percentage: 20, resetsIn: '4h 54m' },
  weekly: { percentage: 51, resetsAt: 'Mon 2:59 PM' },
  today: { messages: 6, tokens: 753200, estimatedCost: 2.47 }
}
```

## UI Reference

```
┌─────────────────────────────────────┐
│  Claude Usage               Pro     │
├─────────────────────────────────────┤
│  ⏱ 5-Hour Window           20%     │
│  ████░░░░░░░░░░░░░░░░░             │
│  Resets in 4h 54m                   │
├─────────────────────────────────────┤
│  📅 Weekly                  51%     │
│  ██████████░░░░░░░░░░░             │
│  Resets Mon 2:59 PM                 │
├─────────────────────────────────────┤
│  📊 Today                           │
│  Messages:                      6   │
│  Tokens:                    753.2K  │
│  Est. Cost:                 $2.47   │
└─────────────────────────────────────┘
```

## Constraints

- **DO NOT** implement real ~/.claude/ parsing yet
- **DO NOT** implement skills section yet
- **DO NOT** implement Tessl integration yet
- Settings button can be a placeholder (no functionality)

## Verification

```bash
cd app && npm start
# Popover shows usage stats with progress bars
# All values are hardcoded mock data
```
