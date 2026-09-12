# Aider Conventions Repository

This repository is a collection of community-contributed convention files for use with [aider](https://aider.chat), an AI pair programming tool. Convention files help guide the AI to follow specific coding styles, practices, and preferences.

## What are Convention Files?

Convention files are markdown files that specify coding guidelines for aider to follow. They can include preferences like:
- Coding style rules
- Preferred libraries and packages
- Type hint requirements
- Testing conventions
- Documentation standards
- And more

For more information about using conventions with aider, see the [conventions documentation](https://aider.chat/docs/usage/conventions.html).

## How to Use These Conventions

1. Browse the subdirectories to find a conventions file that matches your needs
2. Copy the desired `CONVENTIONS.md` to your project
3. Load it in aider using either:
   ```bash
   aider --read-only CONVENTIONS.md
   ```
   Or add it to your `.aider.conf.yml`:
   ```yaml
   read-only: CONVENTIONS.md
   ```

## Directory Structure

Each subdirectory contains:
- `README.md` - Explains the purpose and use case for the conventions
- `CONVENTIONS.md` - The actual conventions file to use with aider

## Contributing

We welcome contributions! To add your own conventions:

1. Create a new subdirectory with a descriptive name
2. Include both a `README.md` explaining your conventions and a `CONVENTIONS.md` file
3. Submit a Pull Request

Please ensure your README.md clearly explains:
- The purpose of your conventions
- What kind of projects they're best suited for
- Any special instructions for using them

