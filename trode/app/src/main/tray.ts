import { Tray, BrowserWindow, nativeImage } from 'electron';
import path from 'path';

let tray: Tray | null = null;
let window: BrowserWindow | null = null;

const WINDOW_WIDTH = 360;
const WINDOW_HEIGHT = 520;

export function getWindow(): BrowserWindow | null {
  return window;
}

function createWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: WINDOW_WIDTH,
    height: WINDOW_HEIGHT,
    show: false,
    frame: false,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    closable: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    backgroundColor: '#0a0a0b',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Load the renderer
  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    win.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  // Hide window when it loses focus
  win.on('blur', () => {
    win.hide();
  });

  return win;
}

function positionWindowNearTray(win: BrowserWindow, trayBounds: Electron.Rectangle) {
  const { x, y, width, height } = trayBounds;
  const winBounds = win.getBounds();

  // Position window below tray icon, centered horizontally
  const posX = Math.round(x + width / 2 - winBounds.width / 2);
  const posY = Math.round(y + height + 4);

  win.setPosition(posX, posY, false);
}

function toggleWindow() {
  if (!window) {
    window = createWindow();
  }

  if (window.isVisible()) {
    window.hide();
  } else {
    const trayBounds = tray?.getBounds();
    if (trayBounds) {
      positionWindowNearTray(window, trayBounds);
    }
    window.show();
    window.focus();
  }
}

export function createTray() {
  // Load icon from file
  const iconPath = path.join(__dirname, '../../assets/tray-iconTemplate.png');
  const icon = nativeImage.createFromPath(iconPath);

  tray = new Tray(icon);
  tray.setTitle('T'); // Show "T" text in menu bar
  tray.setToolTip('Trode - Claude Code Monitor');

  tray.on('click', () => {
    toggleWindow();
  });

  tray.on('right-click', () => {
    toggleWindow();
  });
}
