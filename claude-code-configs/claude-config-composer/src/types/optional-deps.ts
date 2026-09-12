/**
 * Type definitions for optional dependencies
 * These modules may not be available at runtime, so all interfaces are marked as optional
 */

export interface BoxenOptions {
  padding?: number | { top?: number; right?: number; bottom?: number; left?: number };
  margin?: number | { top?: number; right?: number; bottom?: number; left?: number };
  borderStyle?:
    | 'single'
    | 'double'
    | 'round'
    | 'bold'
    | 'singleDouble'
    | 'doubleSingle'
    | 'classic';
  borderColor?: string;
  backgroundColor?: string;
  align?: 'left' | 'center' | 'right';
  float?: 'left' | 'center' | 'right';
  width?: number;
  height?: number;
  fullscreen?: boolean;
}

export type BoxenFunction = (text: string, options?: BoxenOptions) => string;

export interface CFontsOptions {
  font?: string;
  align?: 'left' | 'center' | 'right';
  colors?: string[];
  background?: string;
  letterSpacing?: number;
  lineHeight?: number;
  space?: boolean;
  maxLength?: number;
  gradient?: boolean;
  independentGradient?: boolean;
  transitionGradient?: boolean;
  env?: 'node' | 'browser';
}

export interface CFontsResult {
  string: string;
  array: string[];
  lines: number;
  options: CFontsOptions;
}

export interface CFonts {
  render(text: string, options?: CFontsOptions): CFontsResult;
  say(text: string, options?: CFontsOptions): void;
}

export interface GradientStringFunction {
  (text: string): string;
  atlas: (text: string) => string;
  cristal: (text: string) => string;
  teen: (text: string) => string;
  mind: (text: string) => string;
  morning: (text: string) => string;
  vice: (text: string) => string;
  passion: (text: string) => string;
  fruit: (text: string) => string;
  instagram: (text: string) => string;
  retro: (text: string) => string;
  summer: (text: string) => string;
  rainbow: (text: string) => string;
  pastel: (text: string) => string;
}

export interface FigletOptions {
  font?: string;
  horizontalLayout?: 'default' | 'full' | 'fitted' | 'controlled smushing' | 'universal smushing';
  verticalLayout?: 'default' | 'full' | 'fitted' | 'controlled smushing' | 'universal smushing';
  width?: number;
  whitespaceBreak?: boolean;
}

export type FigletCallback = (err: Error | null, data?: string) => void;

export interface Figlet {
  text(input: string, options: FigletOptions, callback: FigletCallback): void;
  text(input: string, callback: FigletCallback): void;
  textSync(input: string, options?: FigletOptions): string;
}

export interface ChalkAnimationInstance {
  start(): ChalkAnimationInstance;
  stop(): ChalkAnimationInstance;
  render(): void;
  replace(text: string): void;
  frame: string;
}

export interface ChalkAnimation {
  rainbow(text: string, speed?: number): ChalkAnimationInstance;
  pulse(text: string, speed?: number): ChalkAnimationInstance;
  glitch(text: string, speed?: number): ChalkAnimationInstance;
  radar(text: string, speed?: number): ChalkAnimationInstance;
  neon(text: string, speed?: number): ChalkAnimationInstance;
  karaoke(text: string, speed?: number): ChalkAnimationInstance;
}

export interface SpinnerOptions {
  text?: string;
  color?: 'black' | 'red' | 'green' | 'yellow' | 'blue' | 'magenta' | 'cyan' | 'white' | 'gray';
}

export interface Spinner {
  start(options?: { text?: string }): void;
  stop(options?: { text?: string; mark?: '✓' | '✖' | '⚠' | string }): void;
  update(options?: { text?: string }): void;
  success(options?: { text?: string }): void;
  error(options?: { text?: string }): void;
  warn(options?: { text?: string }): void;
  clear(): void;
}

export type CreateSpinnerFunction = (options?: SpinnerOptions) => Spinner;

export interface ProgressBarOptions {
  format?: string;
  fps?: number;
  stream?: NodeJS.WriteStream;
  clearOnComplete?: boolean;
  barCompleteChar?: string;
  barIncompleteChar?: string;
  hideCursor?: boolean;
  linewrap?: boolean;
  etaBuffer?: number;
  synchronousUpdate?: boolean;
  noTTYOutput?: boolean;
  notTTYSchedule?: number;
  barsize?: number;
  position?: 'center' | 'left' | 'right';
  barGlue?: string;
  autopadding?: boolean;
  autopaddingChar?: string;
  gracefulExit?: boolean;
  stopOnComplete?: boolean;
  forceRedraw?: boolean;
}

export interface ProgressBar {
  start(total: number, startValue?: number, payload?: Record<string, unknown>): void;
  update(current: number, payload?: Record<string, unknown>): void;
  increment(delta?: number, payload?: Record<string, unknown>): void;
  setTotal(total: number): void;
  stop(): void;
  getTotalProgress(): number;
  getProgress(): number;
}

export interface MultiBarOptions extends ProgressBarOptions {
  align?: 'left' | 'center' | 'right';
}

export interface MultiBar {
  create(total: number, startValue?: number, payload?: Record<string, unknown>): ProgressBar;
  remove(bar: ProgressBar): boolean;
  stop(): void;
}

export interface CliProgress {
  SingleBar: new (options?: ProgressBarOptions) => ProgressBar;
  MultiBar: new (options?: MultiBarOptions) => MultiBar;
  Presets: {
    shades_classic: ProgressBarOptions;
    shades_grey: ProgressBarOptions;
    legacy: ProgressBarOptions;
    rect: ProgressBarOptions;
  };
}

export interface NodeEmoji {
  get(name: string): string;
  has(name: string): boolean;
  which(emoji: string): string[];
  strip(str: string): string;
  replace(str: string, replacement: string | ((match: string) => string)): string;
  random(): { key: string; emoji: string };
  search(keyword: string): Array<{ key: string; emoji: string }>;
  emojify(str: string): string;
  unemojify(str: string): string;
}

export interface TerminalLinkOptions {
  fallback?: boolean | ((text: string, url: string) => string);
}

export interface TerminalLinkFunction {
  (text: string, url: string, options?: TerminalLinkOptions): string;
  stderr(text: string, url: string, options?: TerminalLinkOptions): string;
  isSupported: boolean;
}

// Error type for optional dependency loading
export interface OptionalDependencyError extends Error {
  code?: string;
  module?: string;
}

// Union types for actual runtime values
export type OptionalBoxen = BoxenFunction | null;
export type OptionalCFonts = CFonts | null;
export type OptionalGradientString = GradientStringFunction | null;
export type OptionalFiglet = Figlet | null;
export type OptionalChalkAnimation = ChalkAnimation | null;
export type OptionalCreateSpinner = CreateSpinnerFunction | null;
export type OptionalCliProgress = CliProgress | null;
export type OptionalNodeEmoji = NodeEmoji | null;
export type OptionalTerminalLink = TerminalLinkFunction | null;
