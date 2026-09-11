# Task: Scaffold Electron Menu Bar App

## Goal

Create a minimal Electron menu bar app with a React popover that shows placeholder text.

## Definition of Done

- [ ] Running `npm start` from `app/` directory launches the app
- [ ] Menu bar shows a tray icon (can use placeholder icon)
- [ ] Clicking tray icon opens a 320px wide popover window
- [ ] Popover has dark theme background (#1a1a1a)
- [ ] Popover shows "Trode" title text
- [ ] No dock icon appears (LSUIElement configured)
- [ ] "Quit" button closes the app cleanly
- [ ] No TypeScript or build errors

## Files to Create

```
app/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── electron-builder.json
├── src/
│   ├── main/
│   │   ├── index.ts
│   │   └── tray.ts
│   ├── preload/
│   │   └── index.ts
│   └── renderer/
│       ├── index.html
│       ├── index.tsx
│       ├── App.tsx
│       └── styles.css
```

## Technical Notes

- Use vite-plugin-electron for Electron + Vite integration
- Reference https://github.com/Iamshankhadeep/ccseva for tray patterns
- Popover should appear below/near the tray icon
- Use BrowserWindow with frame: false

## Constraints

- **DO NOT** implement usage tracking yet
- **DO NOT** implement skills scanning yet
- **DO NOT** implement Tessl integration yet
- Just get a working shell that opens and closes

## Verification

```bash
cd app && npm install && npm start
# Should see tray icon, click opens dark popover, quit works
```
