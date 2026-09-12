import chalk from 'chalk';
import type {
  OptionalBoxen,
  OptionalChalkAnimation,
  OptionalCliProgress,
  OptionalCreateSpinner,
  OptionalFiglet,
  OptionalGradientString,
  OptionalTerminalLink,
} from '../types/optional-deps';

// Try to load optional visual dependencies with fallbacks
let gradient: OptionalGradientString;
let rainbow: ((text: string) => string) | null;
let figlet: OptionalFiglet;
let boxen: OptionalBoxen;
let chalkAnimation: OptionalChalkAnimation;
let createSpinner: OptionalCreateSpinner;
let cliProgress: OptionalCliProgress;
let terminalLink: OptionalTerminalLink;
let hasVisuals = false;

try {
  const gradientModule = require('gradient-string');
  gradient = gradientModule.default || gradientModule;
  rainbow = gradientModule.rainbow;
  figlet = require('figlet');
  boxen = require('boxen');
  chalkAnimation = require('chalk-animation');
  const nanospinnerModule = require('nanospinner');
  createSpinner = nanospinnerModule.createSpinner;
  cliProgress = require('cli-progress');
  terminalLink = require('terminal-link');
  hasVisuals = true;
} catch {
  // Optional dependencies not available, provide fallbacks
  gradient = null;
  rainbow = (text: string) => chalk.white(text);
  figlet = null;
  boxen = null;
  chalkAnimation = null;
  createSpinner = null;
  cliProgress = null;
  terminalLink = null;
}

// Helper function to create gradient or fallback
function createGradientOrFallback(
  colors: string[],
  fallbackColor: string
): (text: string) => string {
  if (gradient && typeof gradient === 'function') {
    try {
      const gradientFn = gradient as unknown as (colors: string[]) => (text: string) => string;
      return gradientFn(colors);
    } catch {
      return (text: string) => chalk.hex(fallbackColor)(text);
    }
  }
  return (text: string) => chalk.hex(fallbackColor)(text);
}

// Beautiful gradients - using brand colors
export const gradients: Record<string, (text: string) => string> = {
  claude: createGradientOrFallback(['#EB6359', '#E2DDD9', '#1F1F25'], '#EB6359'),
  nextjs: createGradientOrFallback(['#1F1F25', '#E2DDD9'], '#1F1F25'),
  react: createGradientOrFallback(['#3B82F6', '#1F1F25'], '#3B82F6'),
  success: createGradientOrFallback(['#0A8310', '#61C466'], '#0A8310'),
  error: createGradientOrFallback(['#E50B0F', '#EA3C3F'], '#E50B0F'),
  info: createGradientOrFallback(['#9A5CF5', '#3B82F6'], '#9A5CF5'),
  fire: createGradientOrFallback(['#EB6359', '#D84D3A', '#C23624'], '#EB6359'),
  rainbow: rainbow || ((text: string) => chalk.white(text)),
  cosmic: createGradientOrFallback(['#9A5CF5', '#EB6359', '#3B82F6'], '#9A5CF5'),
  ocean: createGradientOrFallback(['#1F1F25', '#4C4C51', '#707074'], '#1F1F25'),
  sunset: createGradientOrFallback(['#EB6359', '#F0AFA7', '#FDEBE9'], '#EB6359'),
};

// ASCII Art Banner
export async function showBanner(): Promise<void> {
  return new Promise(resolve => {
    if (!figlet || !hasVisuals) {
      // Fallback banner when figlet is not available
      console.log(chalk.red.bold('\n🚀 Claude Composer'));
      console.log(chalk.gray('✨ Generate Claude Code configurations\n'));
      resolve();
      return;
    }

    figlet.text(
      'Claude\nComposer',
      {
        font: 'ANSI Shadow',
        horizontalLayout: 'default',
        verticalLayout: 'default',
        width: 80,
        whitespaceBreak: true,
      },
      (err: Error | null, data?: string) => {
        if (!err && data) {
          console.log(gradients.claude(data));
          console.log(gradients.cosmic('  ✨ Generate Claude Code configurations\n'));
        } else {
          // Fallback if figlet fails
          console.log(chalk.red.bold('\n🚀 Claude Composer'));
          console.log(chalk.gray('✨ Generate Claude Code configurations\n'));
        }
        resolve();
      }
    );
  });
}

// Mini banner for success
export async function showMiniLogo(): Promise<void> {
  return new Promise(resolve => {
    if (!figlet || !hasVisuals) {
      // Fallback success message when figlet is not available
      console.log(chalk.green.bold('\n✅ SUCCESS!'));
      resolve();
      return;
    }

    figlet.text(
      'SUCCESS!',
      {
        font: 'Small',
        horizontalLayout: 'default',
      },
      (err: Error | null, data?: string) => {
        if (!err && data) {
          console.log('\n' + gradients.success(data));
        } else {
          // Fallback if figlet fails
          console.log(chalk.green.bold('\n✅ SUCCESS!'));
        }
        resolve();
      }
    );
  });
}

// Animated text effects
export function animateText(
  text: string,
  type: 'rainbow' | 'pulse' | 'glitch' | 'radar' | 'neon' | 'karaoke' = 'rainbow'
) {
  if (!chalkAnimation) {
    console.log(chalk.white(text));
    return {
      stop: () => {
        /* no-op */
      },
    };
  }
  const animation = chalkAnimation[type](text);
  return animation;
}

// Pretty box for important messages
export function showBox(
  content: string,
  title?: string,
  type: 'success' | 'error' | 'info' | 'warning' = 'info'
) {
  const colors = {
    success: '#0A8310', // Brand success green
    error: '#E50B0F', // Brand error red
    info: '#EB6359', // Prosperous Red for info
    warning: '#EB6359', // Prosperous Red for warning (as per guidelines)
  };

  if (!boxen) {
    return `\n--- ${title || ''} ---\n${content}\n`;
  }

  const options = {
    padding: 1,
    margin: 1,
    borderStyle: 'round' as const,
    borderColor: colors[type],
    backgroundColor: '#000000',
    title,
    titleAlignment: 'center' as const,
  };

  return boxen(content, options);
}

// Brand colors for syntax highlighting
export const syntaxColors = {
  keyword: '#9A5CF5', // Purple for const, await, etc.
  string: '#10B981', // Green for strings
  comment: '#6B7280', // Gray for comments
  variable: '#F3F4F6', // Light for variables
  function: '#3B82F6', // Blue for functions
  error: '#E50B0F', // Error red
  success: '#0A8310', // Success green
  warning: '#EB6359', // Warning (Prosperous Red)
};

// Custom spinner with fun animations
export function createFunSpinner(text: string) {
  if (!createSpinner) {
    return {
      start: () => console.log(chalk.blue('⚡'), text),
      success: (opts?: { text?: string }) => console.log(chalk.green('✅'), opts?.text || 'Done'),
      error: (opts?: { text?: string }) => console.log(chalk.red('❌'), opts?.text || 'Failed'),
      update: () => {
        /* no-op */
      },
      stop: () => {
        /* no-op */
      },
      warn: () => {
        /* no-op */
      },
      clear: () => {
        /* no-op */
      },
    };
  }
  const spinner = createSpinner({ text });
  return spinner;
}

// Progress bar for file operations
export function createProgressBar(title: string, total: number) {
  if (!cliProgress) {
    return {
      start: () => console.log(chalk.hex('#EB6359')(title), 'Starting...'),
      update: (current: number) => console.log(`Progress: ${current}/${total}`),
      stop: () => console.log('Complete!'),
      getTotalProgress: () => 0,
      getProgress: () => 0,
      increment: () => {
        /* no-op */
      },
      setTotal: () => {
        /* no-op */
      },
    };
  }

  const bar = new cliProgress.SingleBar({
    format: `${chalk.hex('#EB6359')(title)} |${chalk.hex('#EB6359')('{bar}')}| {percentage}% | {value}/{total} Files | ETA: {eta_formatted}`,
    barCompleteChar: '\u2588',
    barIncompleteChar: '\u2591',
    hideCursor: true,
    stopOnComplete: true,
    clearOnComplete: true,
  });

  return bar;
}

// Fancy selection indicator
export function formatChoice(text: string, emoji: string = '🎯') {
  return `${emoji}  ${chalk.bold(text)}`;
}

// Success celebration
export async function celebrate() {
  const frames = ['🎉', '🎊', '✨', '💫', '⭐', '🌟', '💖', '🎈', '🎆', '🎇'];

  let i = 0;
  const interval = setInterval(() => {
    process.stdout.write(
      `\r${frames[i % frames.length]}  Configuration generated successfully!  ${frames[(i + 1) % frames.length]}`
    );
    i++;
  }, 100);

  await new Promise(resolve => setTimeout(resolve, 2000));
  clearInterval(interval);
  process.stdout.write('\r' + ' '.repeat(50) + '\r');
}

// Loading animation with custom messages
export async function showLoadingAnimation(messages: string[], duration: number = 3000) {
  const spinner = createFunSpinner(messages[0]);
  spinner.start();

  let messageIndex = 0;
  const interval = setInterval(() => {
    messageIndex = (messageIndex + 1) % messages.length;
    spinner.update({ text: messages[messageIndex] });
  }, duration / messages.length);

  await new Promise(resolve => setTimeout(resolve, duration));
  clearInterval(interval);
  spinner.success({ text: 'Ready!' });
}

// Pretty section divider
export function divider(char: string = '━', length: number = 60) {
  return chalk.dim(char.repeat(length));
}

// Format file tree with icons
export function formatFileTree(indent: number = 0): string {
  const tree = `
${' '.repeat(indent)}📁 .claude/
${' '.repeat(indent)}├── 📄 CLAUDE.md
${' '.repeat(indent)}└── 📁 .claude/
${' '.repeat(indent)}    ├── ⚙️  settings.json
${' '.repeat(indent)}    ├── 🤖 agents/
${' '.repeat(indent)}    ├── 💻 commands/
${' '.repeat(indent)}    └── 🔧 hooks/`;

  return gradients.ocean(tree);
}

// Typewriter effect
export async function typewrite(text: string, speed: number = 50) {
  for (let i = 0; i < text.length; i++) {
    process.stdout.write(text[i]);
    await new Promise(resolve => setTimeout(resolve, speed));
  }
  console.log();
}

// Pretty error display
export function showError(message: string, suggestion?: string) {
  if (!boxen) {
    console.log('\n' + chalk.red('⚠️  ' + message));
    if (suggestion) {
      console.log(chalk.yellow('💡 ' + suggestion));
    }
    return;
  }

  console.log(
    '\n' +
      boxen(
        chalk.red('⚠️  ' + message) + (suggestion ? '\n\n' + chalk.yellow('💡 ' + suggestion) : ''),
        {
          padding: 1,
          borderStyle: 'double' as const,
          borderColor: 'red',
        }
      )
  );
}

// Pretty list formatting
export function formatList(items: string[], bullet: string = '•') {
  return items.map(item => `  ${chalk.hex('#EB6359')(bullet)} ${item}`).join('\n');
}

// Link formatting
export function createLink(text: string, url: string) {
  if (!terminalLink) {
    return `${chalk.hex('#EB6359').underline(text)} (${url})`;
  }
  return terminalLink(chalk.hex('#EB6359').underline(text), url, {
    fallback: (text: string, url: string) => `${text} (${url})`,
  });
}

// Config count badge
export function showConfigBadge(count: number) {
  const badge = `[${count} configs]`;
  return chalk.bgHex('#EB6359').hex('#FFFFFF').bold(` ${badge} `);
}

// Status indicators
export const status = {
  success: chalk.hex('#0A8310')('✔'), // Brand success green
  error: chalk.hex('#E50B0F')('✖'), // Brand error red
  warning: chalk.hex('#EB6359')('⚠'), // Prosperous Red for warning
  info: chalk.hex('#EB6359')('ℹ'), // Prosperous Red for info
  processing: chalk.hex('#EB6359')('⚡'), // Prosperous Red for processing
  complete: chalk.hex('#0A8310')('✨'), // Brand success green
};

// Fun loading messages
export const loadingMessages = {
  initializing: [
    '🚀 Warming up the fusion reactor...',
    '🔮 Consulting the configuration oracle...',
    '🎭 Preparing the merge...',
    '🌟 Aligning the stars...',
    '⚡ Charging flux capacitors...',
  ],
  merging: [
    '🔀 Merging configurations with love...',
    '🎨 Painting your perfect setup...',
    '🧙‍♂️ Casting configuration spells...',
    '🏗️ Building your dream stack...',
    '✨ Applying configurations...',
  ],
  generating: [
    '📝 Writing beautiful configs...',
    '🎯 Optimizing configuration...',
    '🚦 Green lights all the way...',
    '🎪 Performing configuration circus...',
    '🌈 Adding colors to your code life...',
  ],
  finishing: [
    '🎁 Wrapping up your gift...',
    '🏁 Crossing the finish line...',
    '🎊 Preparing the celebration...',
    '📦 Boxing everything nicely...',
    '🎉 Almost there, get ready to party...',
  ],
};
