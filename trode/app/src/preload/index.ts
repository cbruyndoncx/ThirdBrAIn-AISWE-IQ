import { contextBridge, ipcRenderer } from 'electron';

// Type for installed skill
interface InstalledSkill {
  name: string;
  path: string;
  description?: string;
  source: 'project' | 'global';
}

// Type for skill evaluation
interface SkillEval {
  skillName: string;
  reviewScore: number | null;
  evalImprovement: number | null;
  hasEval: boolean;
  source: string | null;
}

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  quit: () => ipcRenderer.send('quit-app'),
  scanSkills: (): Promise<InstalledSkill[]> => ipcRenderer.invoke('scan-skills'),
  fetchSkillEvals: (skillNames: string[]): Promise<Record<string, SkillEval>> =>
    ipcRenderer.invoke('fetch-skill-evals', skillNames),
  clearEvalCache: (): Promise<void> => ipcRenderer.invoke('clear-eval-cache'),
});

// Type definitions for the exposed API
declare global {
  interface Window {
    electronAPI: {
      quit: () => void;
      scanSkills: () => Promise<InstalledSkill[]>;
      fetchSkillEvals: (skillNames: string[]) => Promise<Record<string, SkillEval>>;
      clearEvalCache: () => Promise<void>;
    };
  }
}
