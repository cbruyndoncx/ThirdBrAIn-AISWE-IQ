# Tailwind CSS Claude Code Configuration 🎨

A comprehensive Claude Code configuration for building beautiful, responsive, and performant user interfaces with Tailwind CSS, utility-first styling, and modern design systems.

## ✨ Features

This configuration provides:

- **Utility-first CSS mastery** with Tailwind's complete toolkit
- **Responsive design patterns** with mobile-first methodology
- **Design system architecture** with custom colors, spacing, and typography
- **Component composition patterns** using utility classes
- **Dark mode implementation** with seamless theming
- **Performance optimization** with CSS purging and minimal bundles
- **Animation and motion** utilities for engaging interfaces
- **Accessibility best practices** with focus management and semantic HTML

## 📦 Installation

1. Copy the `.claude` directory to your project root:

```bash
cp -r tailwindcss/.claude your-project/
cp tailwindcss/CLAUDE.md your-project/
```

2. Install Tailwind CSS in your project:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Optional: Install additional plugins
npm install -D @tailwindcss/typography @tailwindcss/forms @tailwindcss/aspect-ratio @tailwindcss/container-queries
```

3. The configuration will be automatically loaded when you start Claude Code in your project.

## 🎯 What You Get

### Tailwind CSS Expertise

- **Utility-first methodology** - Building complex components with simple utilities
- **Responsive design mastery** - Mobile-first approach with consistent breakpoints
- **Design system creation** - Custom colors, spacing, typography, and component tokens
- **Performance optimization** - CSS purging, minimal bundles, and efficient styling
- **Dark mode implementation** - Seamless theming with class-based or CSS variable approaches
- **Component patterns** - Reusable utility compositions for common UI elements

### Key Development Areas

| Area | Coverage |
|------|----------|
| **Layout** | Flexbox, Grid, Container queries, Responsive design |
| **Typography** | Font families, sizes, weights, line heights, text styles |
| **Colors** | Custom palettes, semantic tokens, dark mode, opacity |
| **Spacing** | Margin, padding, gap, custom scale, responsive spacing |
| **Borders** | Radius, width, colors, shadows, outlines |
| **Animations** | Transitions, transforms, keyframes, micro-interactions |
| **Components** | Buttons, forms, cards, navigation, complex UI patterns |
| **Performance** | Purging, optimization, bundle size, loading strategies |

## 🚀 Quick Start Examples

### Basic Configuration

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          900: '#0c4a6e',
        }
      }
    },
  },
  plugins: [],
}
```

### Component Examples

```jsx
// Button Component with Variants
function Button({ children, variant = 'primary', size = 'md' }) {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50';
  
  const variants = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
    outline: 'border border-gray-300 bg-transparent hover:bg-gray-50',
  };
  
  const sizes = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4',
    lg: 'h-11 px-6 text-lg',
  };
  
  return (
    <button className={`${baseClasses} ${variants[variant]} ${sizes[size]}`}>
      {children}
    </button>
  );
}

// Responsive Card Component
function Card({ children, hover = false }) {
  return (
    <div className={`
      rounded-lg border border-gray-200 bg-white p-6 shadow-sm
      dark:border-gray-800 dark:bg-gray-900
      ${hover ? 'transition-shadow hover:shadow-md' : ''}
    `}>
      {children}
    </div>
  );
}
```

### Responsive Design

```jsx
// Mobile-First Responsive Layout
function ResponsiveLayout() {
  return (
    <div className="
      px-4 py-8
      sm:px-6 sm:py-12
      md:px-8 md:py-16
      lg:px-12 lg:py-20
      xl:px-16 xl:py-24
    ">
      <div className="
        mx-auto max-w-sm
        sm:max-w-md
        md:max-w-lg
        lg:max-w-4xl
        xl:max-w-6xl
      ">
        <h1 className="
          text-2xl font-bold
          sm:text-3xl
          md:text-4xl
          lg:text-5xl
          xl:text-6xl
        ">
          Responsive Typography
        </h1>
      </div>
    </div>
  );
}
```

## 🔧 Configuration Patterns

### Design System Setup

```javascript
// Advanced Tailwind configuration
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Custom brand colors
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          500: '#0ea5e9',
          600: '#0284c7',
          900: '#0c4a6e',
        },
        // Semantic colors using CSS variables
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### CSS Variables for Theming

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
  }
  
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 84% 4.9%;
  }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50;
  }
  
  .card {
    @apply rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900;
  }
}
```

## 🌓 Dark Mode Implementation

### Class-Based Dark Mode

```jsx
// Theme toggle component
function ThemeToggle() {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark');
  };
  
  return (
    <button
      onClick={toggleTheme}
      className="
        rounded-lg p-2 transition-colors
        hover:bg-gray-100 dark:hover:bg-gray-800
        focus:outline-none focus:ring-2 focus:ring-brand-500
      "
    >
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
}

// Dark mode aware components
function DarkModeCard({ children }) {
  return (
    <div className="
      rounded-lg border bg-white p-6 shadow-sm
      border-gray-200 dark:border-gray-700
      dark:bg-gray-800 dark:text-white
    ">
      {children}
    </div>
  );
}
```

## 📱 Responsive Patterns

### Responsive Grid Systems

```jsx
// Auto-responsive grid
function ResponsiveGrid({ children }) {
  return (
    <div className="
      grid gap-6
      grid-cols-1
      sm:grid-cols-2
      lg:grid-cols-3
      xl:grid-cols-4
    ">
      {children}
    </div>
  );
}

// Container queries for component-level responsiveness
function ContainerAwareCard() {
  return (
    <div className="@container">
      <div className="
        p-4
        @md:p-6
        @lg:p-8
      ">
        <h3 className="
          text-lg
          @md:text-xl
          @lg:text-2xl
        ">
          Container Query Title
        </h3>
      </div>
    </div>
  );
}
```

### Responsive Navigation

```jsx
// Mobile-first navigation
function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <nav className="bg-white shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <img className="h-8 w-8" src="/logo.svg" alt="Logo" />
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-8">
            <a href="/" className="text-gray-700 hover:text-brand-600">Home</a>
            <a href="/about" className="text-gray-700 hover:text-brand-600">About</a>
            <a href="/contact" className="text-gray-700 hover:text-brand-600">Contact</a>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-700 hover:text-brand-600"
            >
              ☰
            </button>
          </div>
        </div>
        
        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden">
            <div className="space-y-1 px-2 pb-3 pt-2">
              <a href="/" className="block px-3 py-2 text-gray-700">Home</a>
              <a href="/about" className="block px-3 py-2 text-gray-700">About</a>
              <a href="/contact" className="block px-3 py-2 text-gray-700">Contact</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
```

## 🎬 Animation and Motion

### Custom Animations

```jsx
// Staggered animation list
function StaggeredList({ items }) {
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div
          key={item.id}
          className={`
            animate-fade-in opacity-0
            [animation-delay:${index * 100}ms]
            [animation-fill-mode:forwards]
          `}
        >
          {item.content}
        </div>
      ))}
    </div>
  );
}

// Interactive hover effects
function InteractiveCard({ children }) {
  return (
    <div className="
      group cursor-pointer overflow-hidden rounded-lg bg-white shadow-sm
      transition-all duration-300 hover:shadow-lg hover:-translate-y-1
    ">
      <div className="
        h-48 bg-gradient-to-r from-blue-500 to-purple-600
        transition-transform duration-300 group-hover:scale-105
      " />
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}
```

### Loading States

```jsx
// Skeleton loading components
function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-lg border border-gray-200 p-6">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  );
}

// Spinner component
function Spinner({ size = 'md' }) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };
  
  return (
    <div className={`${sizes[size]} animate-spin rounded-full border-2 border-gray-300 border-t-brand-600`} />
  );
}
```

## 📊 Performance Optimization

### Content Optimization

```javascript
// Optimized content configuration
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  safelist: [
    // Dynamic classes that might be purged incorrectly
    {
      pattern: /bg-(red|green|blue)-(100|500|900)/,
      variants: ['hover', 'focus'],
    },
  ],
  blocklist: [
    // Classes to never include
    'container',
    'collapsible',
  ],
}
```

### Bundle Size Optimization

```javascript
// Plugin configuration for smaller bundles
module.exports = {
  plugins: [
    require('@tailwindcss/typography')({
      className: 'prose',
      target: 'modern', // Smaller bundle size
    }),
    require('@tailwindcss/forms')({
      strategy: 'class', // Only include when using form-* classes
    }),
  ],
  corePlugins: {
    // Disable unused core plugins
    container: false,
    accessibility: false,
  },
}
```

## 🧪 Testing Integration

### Component Testing with Tailwind Classes

```jsx
// Testing utility classes
import { render, screen } from '@testing-library/react';

describe('Button Component', () => {
  it('applies correct styling classes', () => {
    render(<Button variant="primary">Click me</Button>);
    const button = screen.getByRole('button');
    
    expect(button).toHaveClass('bg-brand-600', 'text-white', 'hover:bg-brand-700');
  });
  
  it('responds to different screen sizes', () => {
    render(<ResponsiveCard />);
    const card = screen.getByTestId('card');
    
    expect(card).toHaveClass('p-4', 'md:p-6', 'lg:p-8');
  });
});
```

### Visual Regression Testing

```javascript
// Storybook configuration for visual testing
export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    viewport: {
      viewports: {
        mobile: { name: 'Mobile', styles: { width: '375px', height: '667px' } },
        tablet: { name: 'Tablet', styles: { width: '768px', height: '1024px' } },
        desktop: { name: 'Desktop', styles: { width: '1024px', height: '768px' } },
      },
    },
  },
};

export const AllVariants = () => (
  <div className="space-y-4">
    <Button variant="primary">Primary Button</Button>
    <Button variant="secondary">Secondary Button</Button>
    <Button variant="outline">Outline Button</Button>
  </div>
);
```

## 🔗 Integration

This configuration works seamlessly with:

- **Next.js 15** - App Router and Server Components styling
- **React/Vue/Svelte** - Component-based architectures
- **shadcn/ui** - Pre-built accessible components
- **Headless UI** - Unstyled, accessible UI primitives
- **Framer Motion** - Animation library integration
- **Storybook** - Component documentation and testing

## 📚 Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com)
- [Headless UI](https://headlessui.com)
- [Heroicons](https://heroicons.com)
- [Tailwind Play](https://play.tailwindcss.com) - Online playground
- [Tailwind Community](https://github.com/tailwindlabs/tailwindcss/discussions)
- [Awesome Tailwind CSS](https://github.com/aniftyco/awesome-tailwindcss)

## 🎨 Design Resources

- [Color palette generators](https://tailwindcss.com/docs/customizing-colors)
- [Typography scale calculator](https://type-scale.com)
- [Spacing scale reference](https://tailwindcss.com/docs/customizing-spacing)
- [Component examples](https://tailwindcomponents.com)
- [Templates and themes](https://tailwindtemplates.co)

---

**Ready to build stunning, responsive interfaces with Claude Code and Tailwind CSS!**

🌟 **Star this configuration** if it accelerates your UI development workflow!
