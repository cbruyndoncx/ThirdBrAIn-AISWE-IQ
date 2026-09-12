import chalk from 'chalk';
import type {
  OptionalBoxen,
  OptionalCFonts,
  OptionalGradientString,
  OptionalNodeEmoji,
} from '../types/optional-deps';

// Try to load optional visual dependencies with fallbacks
let gradient: OptionalGradientString;
let CFonts: OptionalCFonts;
let emoji: OptionalNodeEmoji;
let boxen: OptionalBoxen;
let hasVisuals = false;

try {
  const gradientModule = require('gradient-string');
  gradient = gradientModule.default || gradientModule;
  CFonts = require('cfonts');
  emoji = require('node-emoji');
  boxen = require('boxen');
  hasVisuals = true;
} catch {
  // Optional dependencies not available, provide fallbacks
  gradient = null;
  CFonts = null;
  emoji = null;
  boxen = null;
}

// 3D title
export function show3DTitle() {
  if (!hasVisuals || !CFonts) {
    console.log(chalk.red.bold('\n🚀 Claude Composer'));
    return;
  }

  CFonts.say('Claude|Composer', {
    font: 'block',
    align: 'center',
    colors: ['red', 'white'],
    background: 'transparent',
    letterSpacing: 1,
    lineHeight: 1,
    space: true,
    maxLength: 0,
    gradient: true,
    independentGradient: true,
    transitionGradient: true,
  });
}

// Get motivational quote
export async function getMotivationalQuote(): Promise<string> {
  const quotes = [
    { text: 'Code is poetry written in logic.', author: 'Anonymous' },
    { text: 'Every expert was once a beginner.', author: 'Helen Hayes' },
    { text: 'The only way to do great work is to love what you do.', author: 'Steve Jobs' },
    { text: 'Code never lies, comments sometimes do.', author: 'Ron Jeffries' },
    { text: 'First, solve the problem. Then, write the code.', author: 'John Johnson' },
    { text: 'Experience is the name everyone gives to their mistakes.', author: 'Oscar Wilde' },
    { text: 'The best way to predict the future is to invent it.', author: 'Alan Kay' },
    { text: 'Simplicity is the soul of efficiency.', author: 'Austin Freeman' },
    { text: 'Make it work, make it right, make it fast.', author: 'Kent Beck' },
    {
      text: 'Clean code always looks like it was written by someone who cares.',
      author: 'Robert C. Martin',
    },
  ];

  const quote = quotes[Math.floor(Math.random() * quotes.length)];
  const bulbEmoji = emoji ? emoji.get('bulb') : '💡';
  return `${bulbEmoji} "${chalk.italic(quote.text)}"\n   ${chalk.gray('— ' + quote.author)}`;
}

// Pulse effect for important messages
export async function pulseText(text: string, times: number = 3) {
  for (let i = 0; i < times; i++) {
    process.stdout.write('\r' + chalk.dim(text));
    await new Promise(resolve => setTimeout(resolve, 200));
    process.stdout.write('\r' + chalk.bold(text));
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  console.log();
}

// Loading bar with custom style
export function createLoadingBar(title: string) {
  const frames = [
    '[█              ]',
    '[██             ]',
    '[███            ]',
    '[████           ]',
    '[█████          ]',
    '[██████         ]',
    '[███████        ]',
    '[████████       ]',
    '[█████████      ]',
    '[██████████     ]',
    '[███████████    ]',
    '[████████████   ]',
    '[█████████████  ]',
    '[██████████████ ]',
    '[███████████████]',
  ];

  let i = 0;
  const spinner = setInterval(() => {
    const frame = frames[i % frames.length];
    let gradientTitle: string;
    if (gradient && typeof gradient === 'function') {
      try {
        const gradientFn = (gradient as unknown as (colors: string[]) => (text: string) => string)([
          '#EB6359',
          '#E2DDD9',
          '#1F1F25',
        ]);
        gradientTitle = gradientFn(title);
      } catch {
        gradientTitle = chalk.hex('#EB6359')(title);
      }
    } else {
      gradientTitle = chalk.hex('#EB6359')(title);
    }
    process.stdout.write(`\r${gradientTitle} ${frame} ${Math.floor((i / frames.length) * 100)}%`);
    i++;
  }, 100);

  return {
    stop: () => {
      clearInterval(spinner);
      process.stdout.write('\r' + ' '.repeat(50) + '\r');
    },
  };
}

// Live preview of generated structure
export function showLivePreview(configs: string[]) {
  let title: string;
  if (gradient && typeof gradient === 'function') {
    try {
      const gradientFn = (gradient as unknown as (colors: string[]) => (text: string) => string)([
        '#EB6359',
        '#E2DDD9',
      ]);
      title = gradientFn('LIVE PREVIEW - Your Configuration Blueprint');
    } catch {
      title = chalk.hex('#EB6359')('LIVE PREVIEW - Your Configuration Blueprint');
    }
  } else {
    title = chalk.hex('#EB6359')('LIVE PREVIEW - Your Configuration Blueprint');
  }
  const packageEmoji = emoji ? emoji.get('package') : '📦';
  const robotEmoji = emoji ? emoji.get('robot') : '🤖';
  const zapEmoji = emoji ? emoji.get('zap') : '⚡';
  const gearEmoji = emoji ? emoji.get('gear') : '⚙️';
  const bookEmoji = emoji ? emoji.get('book') : '📚';

  const preview = `
${title}

${chalk.dim('━'.repeat(50))}

${chalk.hex('#EB6359').bold('Selected Stack:')}
${configs.map(c => `  ${packageEmoji} ${c}`).join('\n')}

${chalk.hex('#0A8310').bold('What You Get:')}
  ${robotEmoji} ${chalk.bold(configs.length * 5 + 3)} Specialized AI Agents
  ${zapEmoji} ${chalk.bold(configs.length * 3 + 2)} Custom Commands
  ${gearEmoji} ${chalk.bold(configs.length * 2)} Automation Hooks
  ${bookEmoji} ${chalk.bold(1)} Comprehensive Documentation

${chalk.dim('━'.repeat(50))}
`;

  if (boxen) {
    console.log(
      boxen(preview, {
        padding: 1,
        margin: 1,
        borderStyle: 'double' as const,
        borderColor: '#EB6359', // Prosperous Red
        backgroundColor: '#1F1F25', // Executive Deep
      })
    );
  } else {
    console.log(preview);
  }
}
