# shadcn/ui Claude Code Configuration 🎨

A comprehensive Claude Code configuration for building beautiful, accessible, and customizable UI components with shadcn/ui. This configuration transforms Claude into an expert shadcn/ui developer with deep knowledge of React patterns, Tailwind CSS, Radix UI, and modern accessibility standards.

## ✨ Features

This configuration provides comprehensive shadcn/ui development support:

- **10 Specialized AI Agents** for different aspects of UI development
- **8 Powerful Commands** for component scaffolding and optimization
- **Intelligent Hooks** for automated validation and formatting
- **Optimized Settings** for shadcn/ui workflows
- **Comprehensive Memory** with component patterns and best practices
- **Framework-agnostic** support (Next.js, Vite, Remix, Astro, etc.)

## 📦 Installation

1. Copy the configuration to your shadcn/ui project:

```bash
# Copy the entire configuration
cp -r shadcn/.claude your-project/
cp shadcn/CLAUDE.md your-project/

# Make hook scripts executable (if any)
chmod +x your-project/.claude/hooks/*.sh
```

2. Initialize shadcn/ui in your project (if not already done):

```bash
npx shadcn@latest init
```

3. The configuration will be automatically loaded when you start Claude Code.

## 📁 Configuration Structure

```text
.claude/
├── settings.json           # Main configuration with permissions and hooks
├── agents/                 # Specialized AI subagents
│   ├── component-builder.md       # Component creation specialist
│   ├── accessibility-auditor.md   # A11y compliance expert
│   ├── tailwind-optimizer.md      # Tailwind CSS optimization
│   ├── radix-expert.md            # Radix UI primitives specialist
│   ├── form-specialist.md         # Form and validation expert
│   ├── data-display-expert.md     # Tables and charts specialist
│   ├── theme-designer.md          # Theming and styling expert
│   ├── animation-specialist.md    # Animations and transitions
│   ├── migration-expert.md        # Component migration specialist
│   └── performance-optimizer.md   # Performance optimization
├── commands/               # Custom slash commands
│   ├── add-component.md           # Scaffold new component
│   ├── create-variant.md          # Add component variant
│   ├── setup-form.md              # Set up form with validation
│   ├── create-data-table.md       # Create data table
│   ├── setup-dark-mode.md         # Configure dark mode
│   ├── analyze-accessibility.md   # A11y audit
│   ├── optimize-bundle.md         # Bundle optimization
│   └── migrate-component.md       # Migrate existing components
└── hooks/                  # Automation scripts
    ├── validate-components.sh     # Component validation
    ├── format-tailwind.sh         # Tailwind class sorting
    ├── check-accessibility.sh     # A11y checks
    └── optimize-imports.sh        # Import optimization

CLAUDE.md                   # Main expertise instructions
README.md                   # This file
```

## 🤖 Specialized Agents (10 Expert Agents)

### Core Development Agents

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `component-builder` | Component creation specialist | Building new shadcn/ui components, proper TypeScript types, variant systems |
| `accessibility-auditor` | Accessibility compliance expert | ARIA attributes, keyboard navigation, screen reader support |
| `tailwind-optimizer` | Tailwind CSS specialist | Utility classes, custom CSS properties, responsive design |
| `radix-expert` | Radix UI primitives specialist | Behavior implementation, primitive composition, portal usage |
| `form-specialist` | Form and validation expert | React Hook Form integration, Zod schemas, error handling |

### Advanced Feature Agents

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `data-display-expert` | Tables and charts specialist | TanStack Table, Recharts, data visualization |
| `theme-designer` | Theming and styling expert | CSS variables, color systems, dark mode |
| `animation-specialist` | Animation and transitions expert | Framer Motion, CSS transitions, gesture handling |
| `migration-expert` | Component migration specialist | Converting existing components to shadcn/ui patterns |
| `performance-optimizer` | Performance optimization expert | Bundle size, code splitting, lazy loading |

## 🛠️ Commands (8 Powerful Commands)

| Command | Description | Usage |
|---------|-------------|-------|
| `/add-component` | Scaffold new shadcn/ui component | `/add-component button dialog card` |
| `/create-variant` | Add variant to existing component | `/create-variant button size=xl` |
| `/setup-form` | Set up form with validation | `/setup-form contact-form` |
| `/create-data-table` | Create advanced data table | `/create-data-table users` |
| `/setup-dark-mode` | Configure dark mode | `/setup-dark-mode [next\|vite\|remix]` |
| `/analyze-accessibility` | Run accessibility audit | `/analyze-accessibility` |
| `/optimize-bundle` | Optimize bundle size | `/optimize-bundle` |
| `/migrate-component` | Migrate to shadcn/ui patterns | `/migrate-component Button.jsx` |

## 🪝 Automation Hooks

### Pre-commit Validation

- **Component Structure Validator** (`validate-components.sh`)
  - Validates proper component structure
  - Checks for required TypeScript types
  - Ensures proper forwardRef usage
  - Validates variant system implementation

### Auto-formatting

- **Tailwind Class Sorter** (`format-tailwind.sh`)
  - Sorts Tailwind classes automatically
  - Merges duplicate classes
  - Orders responsive modifiers
  - Groups related utilities

### Accessibility Checks

- **A11y Validator** (`check-accessibility.sh`)
  - Validates ARIA attributes
  - Checks keyboard navigation support
  - Ensures proper focus management
  - Validates color contrast

### Import Optimization

- **Import Optimizer** (`optimize-imports.sh`)
  - Removes unused imports
  - Orders imports consistently
  - Groups related imports
  - Validates component exports

## ⚙️ Configuration Details

### Security Permissions

**Allowed Operations:**
- All file operations in components/ui directory
- NPM commands for component installation
- shadcn CLI commands
- Development server commands
- Testing and linting commands
- Git operations for version control

**Denied Operations:**
- Modifying node_modules
- Deleting core configuration files
- Publishing to npm without review
- Modifying system files

### Environment Variables

Pre-configured for shadcn/ui development:

```env
# Component configuration
SHADCN_STYLE=new-york
SHADCN_RSC=true
SHADCN_TSX=true
SHADCN_CSS_VARIABLES=true
SHADCN_TAILWIND_CONFIG=tailwind.config.js
SHADCN_COMPONENTS_PATH=@/components
SHADCN_UTILS_PATH=@/lib/utils
SHADCN_BASE_COLOR=zinc
```

## 🚀 Usage Examples

### Creating a New Component

```bash
# Add official shadcn/ui component
> /add-component sheet

# Create custom component following shadcn patterns
> Use the component-builder agent to create a custom DateRangePicker component
```

### Setting Up Forms

```bash
# Create a complete form with validation
> /setup-form user-registration

# The command will:
# - Create form component structure
# - Set up React Hook Form
# - Add Zod validation schema
# - Create all form fields
# - Add error handling
```

### Implementing Data Tables

```bash
# Create an advanced data table
> /create-data-table products

# Features included:
# - Sorting and filtering
# - Pagination
# - Row selection
# - Column visibility
# - Export functionality
```

### Dark Mode Setup

```bash
# Configure dark mode for your framework
> /setup-dark-mode next

# Sets up:
# - Theme provider
# - CSS variables
# - Toggle component
# - System preference detection
# - Cookie persistence
```

## 📊 Component Categories

### Form Controls
```tsx
// Comprehensive form component support
<Form>
  <FormField
    control={form.control}
    name="email"
    render={({ field }) => (
      <FormItem>
        <FormLabel>Email</FormLabel>
        <FormControl>
          <Input {...field} />
        </FormControl>
        <FormDescription>Your email address</FormDescription>
        <FormMessage />
      </FormItem>
    )}
  />
</Form>
```

### Overlay Components
```tsx
// Accessible modal patterns
<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

### Data Display
```tsx
// Advanced table with TanStack Table
<DataTable
  columns={columns}
  data={data}
  searchKey="email"
  pagination
  sorting
  filtering
/>
```

## 🎨 Theming System

### CSS Variables
```css
/* Automatic theme switching */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 84% 4.9%;
}
```

### Component Variants
```tsx
// CVA-powered variant system
const buttonVariants = cva(
  "base-classes",
  {
    variants: {
      variant: {
        default: "...",
        destructive: "...",
        outline: "...",
      },
      size: {
        default: "...",
        sm: "...",
        lg: "...",
      }
    }
  }
)
```

## 📝 Best Practices Enforced

1. **Accessibility First** - WCAG 2.1 AA compliance
2. **Type Safety** - Full TypeScript support
3. **Component Composition** - Flexible, reusable patterns
4. **Performance** - Optimized bundle size and runtime
5. **Customization** - Easy to modify and extend
6. **Framework Agnostic** - Works with any React framework
7. **Dark Mode** - Built-in theme support
8. **Mobile First** - Responsive by default

## 🔧 Framework-Specific Support

### Next.js (13-15)
- App Router support
- Server Components compatibility
- Streaming and Suspense
- Metadata API integration

### Vite
- Fast HMR
- Optimized builds
- Tailwind v4 support

### Remix
- Progressive enhancement
- Action/Loader patterns
- Session-based theming

### Astro
- Island architecture
- Partial hydration
- Multi-framework support

## 🐛 Troubleshooting

### Common Issues

**Components not styling correctly:**
```bash
# Verify Tailwind configuration
npx shadcn@latest init

# Check CSS import
# Ensure globals.css is imported in your app
```

**TypeScript errors:**
```bash
# Update TypeScript config
# Ensure paths are configured correctly
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

**Dark mode not working:**
```bash
# Verify theme provider setup
# Check CSS variables are defined
# Ensure class/data attribute is applied to html
```

## 🚀 Quick Start Example

```bash
# 1. Initialize a new Next.js project
npx create-next-app@latest my-app --typescript --tailwind

# 2. Initialize shadcn/ui
cd my-app
npx shadcn@latest init

# 3. Copy Claude configuration
cp -r path/to/shadcn/.claude .
cp path/to/shadcn/CLAUDE.md .

# 4. Add your first components
npx shadcn@latest add button card form

# 5. Start developing with Claude Code
# Claude now has full shadcn/ui expertise!
```

## 📚 Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Component Examples](https://ui.shadcn.com/examples)
- [Radix UI Primitives](https://radix-ui.com)
- [Tailwind CSS](https://tailwindcss.com)
- [React Hook Form](https://react-hook-form.com)
- [Zod Validation](https://zod.dev)

## 🎯 What Makes This Configuration Special

### Complete Development Environment
- **10 Expert Agents** - Specialized AI assistants for every aspect of UI development
- **8 Power Commands** - From component creation to optimization
- **4 Smart Hooks** - Automatic validation, formatting, and optimization
- **Comprehensive Settings** - Pre-configured for shadcn/ui best practices

### Key Capabilities
1. **Component Generation** - Create components following shadcn/ui patterns
2. **Accessibility Compliance** - Built-in WCAG 2.1 AA validation
3. **Performance Optimization** - Automatic bundle and runtime optimization
4. **Framework Support** - Works with Next.js, Vite, Remix, Astro, and more
5. **Theme Management** - Complete dark mode and theming system

### Perfect For
- Building modern React applications with shadcn/ui
- Creating accessible, performant UI components
- Implementing design systems with Tailwind CSS
- Migrating existing components to shadcn/ui patterns
- Learning React component best practices

---

**Built for the modern web** 🚀

*Create beautiful, accessible, and customizable UI components with shadcn/ui and Claude Code.*

**Configuration Version:** 1.0.0 | **Compatible with:** shadcn/ui 0.8+, React 18+, Tailwind CSS 3.4+