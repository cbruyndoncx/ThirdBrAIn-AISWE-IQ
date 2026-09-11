import { app, ipcMain } from 'electron';
import { createTray, getWindow } from './tray';
import { scanForSkills, getProjectPath } from '../services/skillsScanner';
import { fetchSkillEvals, clearEvalCache, SkillEval } from '../services/tesslService';

// Handle IPC events
ipcMain.on('quit-app', () => {
  app.quit();
});

// Handle skills scanning
ipcMain.handle('scan-skills', () => {
  const projectPath = getProjectPath();
  return scanForSkills(projectPath);
});

// Handle skill evaluations lookup
ipcMain.handle('fetch-skill-evals', async (_event, skillNames: string[]) => {
  const evalsMap = await fetchSkillEvals(skillNames);
  // Convert Map to object for IPC serialization
  const result: Record<string, SkillEval> = {};
  evalsMap.forEach((value, key) => {
    result[key] = value;
  });
  return result;
});

// Handle cache clear
ipcMain.handle('clear-eval-cache', () => {
  clearEvalCache();
});

// Hide dock icon on macOS
if (process.platform === 'darwin') {
  app.dock.hide();
}

app.whenReady().then(() => {
  createTray();
});

app.on('window-all-closed', () => {
  // Keep app running even when window is closed (menu bar app)
});

app.on('activate', () => {
  const win = getWindow();
  if (win) {
    win.show();
  }
});
