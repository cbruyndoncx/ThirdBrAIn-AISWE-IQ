# Claude Code Skills Collection

> **As Seen On**: [99% Of Claude Code Skills Don't Actually Work - Here Are Mine That Do](https://www.youtube.com/watch?v=Xzivyr5wXQc)
>
> **Want the skill-creator-plus skill?** Get it from [BuilderPack](https://builderpack.ai/?utm_source=github&utm_medium=readme&utm_campaign=claude_16) or just the [Claude Code Pack](https://builderpack.ai/claude?utm_source=github&utm_medium=readme&utm_campaign=claude_16)

A curated collection of high-quality skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that unlock Claude's capabilities for specialized tasks.

## The Story Behind These Skills

These are skills I actively work on and use in my actual projects and apps. They're not theoretical frameworks—they're battle-tested tools that power my daily workflow.

I started creating these skills out of necessity. Every time I worked with Claude Code, I found myself explaining the same context, repeating the same principles, and course-correcting the same patterns. After iterating on dozens of skills, I distilled the patterns that separate effective skills from fancy checklists. Philosophy-first design, explicit anti-patterns, variation encouragement—these aren't buzzwords, they're the difference between Claude following a template and Claude actually thinking.

I'm sharing these because I believe **great tools should be shared**. Each skill in this collection has saved me hours of repetitive work and produced better outputs than I could have prompted for from scratch.

Use them. Modify them. Build on them. And if you create something great, I'd love to hear about it.

---

## What Are Skills?

Skills are mental frameworks that guide Claude's problem-solving in specific domains. Unlike rigid templates, they establish **how to think** about a problem, not just what to do. Each skill provides:

- **Philosophy**: The mental model for approaching the domain
- **Guidelines**: Actionable advice organized by category
- **Anti-patterns**: Common mistakes to avoid
- **Variation guidance**: How to adapt outputs to context

## Skills at a Glance

| Skill | What | Why |
|-------|------|-----|
| 🎨 **Favicon Generator** | Professional favicons with multi-layer effects | App-quality icons without design tools |
| ✨ **Frontend Design** | Distinctive frontend interfaces with high design quality | Build visually striking UIs that avoid generic AI aesthetics |
| 🖼️ **OG Image Creator** | Brand-aligned social sharing images from codebase | Automatic, contextual OG images that match your brand |
| 🔍 **Site Metadata Generator** | Comprehensive SEO optimization and metadata | Improve search rankings with proper meta tags and structured data |
| 🎬 **YouTube Titles & Thumbnails** | High-CTR title/thumbnail pairs using curiosity frameworks | Maximize clicks without clickbait |

## Installation

Copy the `.claude/skills` folder to your project:

```bash
# Clone this repo
git clone https://github.com/your-username/builderpack-cc-skills.git

# Copy skills to your project
cp -r builderpack-cc-skills/.claude/skills /path/to/your-project/.claude/
```

Or copy individual skills:

```bash
# Copy only the favicon generator
cp -r builderpack-cc-skills/.claude/skills/favicon-generator /path/to/your-project/.claude/skills/
```

Claude Code will automatically load relevant skills based on context and your prompts.

---

## Available Skills

All **5 skills** follow philosophy-first design principles.

### 🎨 Favicon Generator

**What it does**: Generates professional-quality favicons with multi-layer visual effects (drop shadows, inner glows, highlights, gradients, noise) that rival icons from Linear, Notion, and Figma.

**Why use it**: Get polished, app-quality icons without opening a design tool. Automatically discovers and matches your existing brand icons from the codebase.

**You get**: Complete favicon suite (ICO, SVG, PNG at all sizes), apple-touch-icon, PWA images, and framework integration code.

#### Example Prompts

```
Create a favicon for my app using the letter "T" with a modern indigo-purple gradient
```

```
Generate a professional favicon matching my brand. Check my Tailwind config for colors and use the same icon from my Header component
```

```
Make a favicon suite for my developer tool - something minimal and technical looking
```

```
I need favicons for a health/wellness app. Use warm, friendly colors with a heart icon
```

```
Create a neon-style favicon with a terminal icon for my CLI tool
```

---

### ✨ Frontend Design

_Source: [Anthropic Skills Repository](https://github.com/anthropics/skills)_

**What it does**: Creates distinctive frontend interfaces with high design quality that avoid generic "AI slop" aesthetics.

**Why use it**: Build visually striking web components, pages, and applications with bold aesthetic choices. Get polished code with exceptional attention to detail instead of cookie-cutter designs.

**You get**: Functional code with visually striking interfaces, cohesive designs with clear aesthetic direction, and framework-ready integration (HTML/CSS/JS, React, Vue, etc.).

#### Example Prompts

```
Build a landing page for a developer tool with a brutalist aesthetic
```

```
Create a dashboard component with a retro-futuristic vibe using distinctive typography
```

```
Design a product card with maximalist energy - bold colors, unexpected layouts, eye-catching animations
```

```
Make a minimal, refined interface for a meditation app with soft pastel colors and organic shapes
```

```
Build a portfolio hero section with an editorial magazine aesthetic and dramatic typography
```

---

### 🖼️ OG Image Creator

**What it does**: Generates authentic, brand-aligned Open Graph (social sharing) images by analyzing your codebase to extract colors, fonts, and logo, then creating contextually appropriate images for each route.

**Why use it**: Get automatic social sharing previews that match your actual brand (not generic templates). Context-aware designs mean landing pages get different treatments than articles.

**You get**: Analysis JSON with routes and brand identity, OG images (1200x630px) for all routes, framework-specific meta tag code, and platform testing checklist.

#### Example Prompts

```
Analyze my Next.js app and generate OG images for all routes that match my brand
```

```
Create social sharing images for my Astro site. Extract colors from my Tailwind config
```

```
I need OG images for my documentation site. Use the logo from /public/logo.svg
```

```
Generate contextual OG images - landing pages should look different from blog posts
```

```
Create Facebook and Twitter-optimized OG images for my product pages
```

---

### 🔍 Site Metadata Generator

**What it does**: Provides comprehensive SEO optimization for web applications through proper metadata, structured data, and search engine communication.

**Why use it**: Improve search rankings and discoverability with proper meta tags, JSON-LD structured data, and framework-native SEO optimization. Make your content easily understood by search engines and social platforms.

**You get**: Meta tags for all routes, JSON-LD structured data (Schema.org), sitemap.xml and robots.txt, framework-specific integration code, and SEO analysis with recommendations.

#### Example Prompts

```
Analyze my Next.js app and generate comprehensive SEO metadata for all pages
```

```
Add structured data (JSON-LD) for my blog posts to get rich search results
```

```
Optimize my Astro site for SEO - meta tags, sitemap, and proper semantic markup
```

```
Generate Schema.org structured data for my product pages
```

```
Audit my site's SEO and suggest improvements for Core Web Vitals
```

---

### 🎬 YouTube Titles & Thumbnails

**What it does**: Creates high-performing YouTube titles and thumbnail text pairs that maximize CTR and virality while maintaining authenticity using the Curiosity-Value Framework.

**Why use it**: Maximize click-through rates without misleading clickbait. Generates complementary thumbnail + title pairs (not redundant) adapted to your content type.

**You get**: 3-5 title options using different patterns, complementary thumbnail text (3-5 words max), rationale for each option, and trade-off analysis.

#### Example Prompts

```
Here's my video transcript about migrating from React to Vue. Help me create titles and thumbnail text that will drive clicks
```

```
I made a tutorial on Docker for beginners. What titles and thumbnails would work best?
```

```
Analyze this video script and give me 5 title options with complementary thumbnail text
```

```
My video is about why I stopped using Redux after 3 years. Create provocative but honest title/thumbnail pairs
```

```
I have a comparison video: REST vs GraphQL. Help me create titles that create curiosity without being clickbait
```

---

## Quick Reference: Prompt Patterns

### Getting Started

| Goal | Prompt |
|------|--------|
| Use a skill | `"[Task description]"` — Claude loads relevant skills automatically |
| Force a skill | `"Using the [skill-name] skill, [task]"` |
| List skills | `"What skills are available in this project?"` |

### Favicon Generator

| Goal | Prompt |
|------|--------|
| Quick favicon | `"Create a favicon with the letter X"` |
| Match brand | `"Generate a favicon matching my project's colors and icons"` |
| Specific style | `"Make a [modern/vibrant/minimal/glass/neon] favicon"` |
| With icon | `"Create a favicon using the [rocket/terminal/shield] icon"` |

### Frontend Design

| Goal | Prompt |
|------|--------|
| Landing page | `"Build a landing page with a [brutalist/minimalist/maximalist] aesthetic"` |
| Component | `"Create a [dashboard/card/hero] component with [retro/futuristic/editorial] design"` |
| Specific tone | `"Design an interface with [organic/industrial/playful] vibes"` |
| Avoid generic | `"Build a product page that avoids generic AI aesthetics"` |

### OG Image Creator

| Goal | Prompt |
|------|--------|
| Auto-generate all | `"Analyze my codebase and generate OG images for all routes"` |
| Match brand | `"Create OG images using colors from my Tailwind config"` |
| Specific route | `"Generate an OG image for my /about page"` |
| Framework-specific | `"Create OG images for my [Next.js/Astro/Gatsby] site"` |

### Site Metadata Generator

| Goal | Prompt |
|------|--------|
| Full SEO audit | `"Analyze my site and generate comprehensive SEO metadata"` |
| Structured data | `"Add JSON-LD structured data for my [blog/products/events]"` |
| Meta tags | `"Generate proper meta tags for all my routes"` |
| Framework-specific | `"Optimize SEO for my [Next.js/Astro/React] application"` |

### YouTube Titles & Thumbnails

| Goal | Prompt |
|------|--------|
| From transcript | `"Here's my transcript: [paste]. Generate title options"` |
| Specific emotion | `"Create titles that evoke [curiosity/FOMO/ambition]"` |
| Content type | `"This is a [tutorial/analysis/story/comparison] video..."` |
| Improve existing | `"My current title is X. How can I make it more compelling?"` |


## Skill Structure

Each skill follows this directory structure:

```
skill-name/
├── SKILL.md          # Main skill definition (philosophy + guidelines)
├── scripts/          # Executable code for deterministic operations
│   └── tool.py
├── references/       # Detailed documentation for progressive disclosure
│   └── details.md
└── assets/           # Templates, images, fonts used in outputs
    └── template.html
```

### SKILL.md Anatomy

```markdown
---
name: skill-name
description: >
  What the skill does, when to use it, and specific triggers.
---

# Skill Name

## Philosophy: [Core Mental Framework]
Establishes HOW to think before WHAT to do.

## [Main Guidelines]
Organized, actionable guidance.

## Anti-Patterns to Avoid
What NOT to do, with explanations.

## Variation Guidance
How outputs should adapt to context.

## Remember
Empowering conclusion.
```

---

## Contributing

### Adding a New Skill

1. Study existing skills in this repository to understand the philosophy-first approach

2. Create the skill directory structure:
   ```
   .claude/skills/my-skill/
   ├── SKILL.md          # Main skill definition
   ├── references/       # Detailed documentation (optional)
   └── scripts/          # Automation tools (optional)
   ```

3. Write `SKILL.md` following the architecture pattern:
   - Start with philosophy before procedures
   - Include anti-patterns with specific examples
   - Encourage variation and context-specific adaptation
   - Keep it concise (500-700 lines max)

4. Test your skill with Claude Code to ensure it produces the desired outcomes

### Quality Checklist

- [ ] Philosophy section before procedures
- [ ] Explicit anti-patterns with examples
- [ ] Variation encouragement
- [ ] Concrete, specific guidance
- [ ] Empowering (not constraining) tone
- [ ] SKILL.md under 500 lines

---

**Chong-U** | AI Oriented

[![X](https://img.shields.io/badge/X-@chongdashu-000000?style=flat&logo=x)](https://www.x.com/chongdashu)
[![YouTube](https://img.shields.io/badge/YouTube-@AIOriented-FF0000?style=flat&logo=youtube)](https://www.youtube.com/@AIOriented)
