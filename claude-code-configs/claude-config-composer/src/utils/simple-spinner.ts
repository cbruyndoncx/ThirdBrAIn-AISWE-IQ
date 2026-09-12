/**
 * Simple spinner implementation to avoid ESM module issues
 * This replaces ora to ensure compatibility with all Node.js versions
 */
export class SimpleSpinner {
  private message: string;
  private timer: NodeJS.Timeout | null = null;
  private frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  private currentFrame = 0;
  private stream = process.stderr;
  private isSpinning = false;

  constructor(message: string) {
    this.message = message;
  }

  start(newMessage?: string): SimpleSpinner {
    if (newMessage) {
      this.message = newMessage;
    }
    if (this.isSpinning) return this;

    this.isSpinning = true;
    this.stream.write(`- ${this.message}`);

    // Only animate if we have a TTY (not in CI)
    if (this.stream.isTTY) {
      this.timer = setInterval(() => {
        this.currentFrame = (this.currentFrame + 1) % this.frames.length;
        this.stream.write(`\r${this.frames[this.currentFrame]} ${this.message}`);
      }, 80);
    }

    return this;
  }

  succeed(text?: string): SimpleSpinner {
    this.stop();
    const finalText = text || this.message;
    if (this.stream.isTTY) {
      this.stream.write(`\r✔ ${finalText}\n`);
    } else {
      this.stream.write(`\n✔ ${finalText}\n`);
    }
    return this;
  }

  fail(text?: string): SimpleSpinner {
    this.stop();
    const finalText = text || this.message;
    if (this.stream.isTTY) {
      this.stream.write(`\r✖ ${finalText}\n`);
    } else {
      this.stream.write(`\n✖ ${finalText}\n`);
    }
    return this;
  }

  warn(text?: string): SimpleSpinner {
    this.stop();
    const finalText = text || this.message;
    if (this.stream.isTTY) {
      this.stream.write(`\r⚠ ${finalText}\n`);
    } else {
      this.stream.write(`\n⚠ ${finalText}\n`);
    }
    return this;
  }

  set text(newText: string) {
    this.message = newText;
    if (this.isSpinning && this.stream.isTTY) {
      this.stream.write(`\r${this.frames[this.currentFrame]} ${this.message}`);
    }
  }

  get text(): string {
    return this.message;
  }

  private stop(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.isSpinning = false;
  }
}

export function createSpinner(message: string): SimpleSpinner {
  return new SimpleSpinner(message);
}
