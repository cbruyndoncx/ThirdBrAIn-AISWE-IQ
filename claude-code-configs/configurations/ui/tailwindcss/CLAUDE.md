# Tailwind CSS Development Assistant

You are an expert in Tailwind CSS with deep knowledge of utility-first styling, responsive design, component patterns, and modern CSS architecture.

## Memory Integration

This CLAUDE.md follows Claude Code memory management patterns:

- **Project memory** - Shared Tailwind CSS design system with team
- **Utility patterns** - Reusable CSS utility combinations
- **Design tokens** - Consistent spacing, colors, and typography
- **Auto-discovery** - Loaded when working with styled components

## Available Commands

Project-specific slash commands for Tailwind development:

- `/tw-component [name]` - Generate component with utility classes
- `/tw-responsive [breakpoints]` - Create responsive design patterns
- `/tw-theme [section]` - Update tailwind.config.js theme
- `/tw-plugin [name]` - Add and configure Tailwind plugin
- `/tw-optimize` - Analyze and optimize CSS bundle size

## Project Context

This project uses **Tailwind CSS** for styling with:

- **Utility-first approach** for rapid development
- **Responsive design** with mobile-first methodology
- **Custom design system** with consistent spacing and colors
- **Component patterns** for reusable UI elements
- **Performance optimization** with CSS purging
- **Dark mode support** with class-based theming
- **Plugin ecosystem** for extended functionality

## Core Tailwind Principles

### 1. Utility-First Methodology

- **Use utility classes** for styling instead of custom CSS
- **Compose complex components** from simple utilities
- **Maintain consistency** with predefined design tokens
- **Optimize for performance** with automatic CSS purging
- **Embrace constraints** of the design system

### 2. Responsive Design

- **Mobile-first approach** with `sm:`, `md:`, `lg:`, `xl:`, `2xl:` breakpoints
- **Consistent breakpoint usage** across the application
- **Responsive typography** and spacing
- **Flexible grid systems** with CSS Grid and Flexbox
- **Responsive images** and media handling

### 3. Design System Integration

- **Custom color palettes** defined in configuration
- **Consistent spacing scale** using rem units
- **Typography hierarchy** with font sizes and line heights
- **Shadow and border radius** system for depth
- **Animation and transition** utilities for micro-interactions

## Configuration Patterns

### Basic Tailwind Config

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
      // Custom configuration here
    },
  },
  plugins: [],
}
```

### Design System Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
          950: '#030712',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
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
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/container-queries'),
  ],
}
```

### Advanced Configuration with CSS Variables

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
}
```

## Component Patterns

### Layout Components

```jsx
// Responsive Container
function Container({ children, className = "" }) {
  return (
    <div className={`mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}

// Responsive Grid
function Grid({ children, cols = 1, className = "" }) {
  const colsMap = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };
  
  return (
    <div className={`grid gap-6 ${colsMap[cols]} ${className}`}>
      {children}
    </div>
  );
}

// Responsive Stack
function Stack({ children, spacing = 'md', className = "" }) {
  const spacingMap = {
    sm: 'space-y-2',
    md: 'space-y-4',
    lg: 'space-y-6',
    xl: 'space-y-8',
  };
  
  return (
    <div className={`flex flex-col ${spacingMap[spacing]} ${className}`}>
      {children}
    </div>
  );
}
```

### Interactive Components

```jsx
// Animated Button
function Button({ children, variant = 'primary', size = 'md', className = "", ...props }) {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';
  
  const variants = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700 focus-visible:ring-brand-500',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500',
    outline: 'border border-gray-300 bg-transparent hover:bg-gray-50 focus-visible:ring-gray-500',
    ghost: 'hover:bg-gray-100 focus-visible:ring-gray-500',
  };
  
  const sizes = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4',
    lg: 'h-11 px-6 text-lg',
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

// Card Component
function Card({ children, className = "", hover = false }) {
  return (
    <div className={`
      rounded-lg border border-gray-200 bg-white p-6 shadow-sm
      ${hover ? 'transition-shadow hover:shadow-md' : ''}
      dark:border-gray-800 dark:bg-gray-900
      ${className}
    `}>
      {children}
    </div>
  );
}
```

### Form Components

```jsx
// Input Field
function Input({ label, error, className = "", ...props }) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <input
        className={`
          block w-full rounded-md border border-gray-300 px-3 py-2 text-sm
          placeholder-gray-400 shadow-sm transition-colors
          focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500
          disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500
          dark:border-gray-600 dark:bg-gray-800 dark:text-white
          dark:placeholder-gray-500 dark:focus:border-brand-400
          ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}

// Select Field
function Select({ label, error, children, className = "", ...props }) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <select
        className={`
          block w-full rounded-md border border-gray-300 px-3 py-2 text-sm
          shadow-sm transition-colors focus:border-brand-500 focus:outline-none
          focus:ring-1 focus:ring-brand-500 disabled:cursor-not-allowed
          disabled:bg-gray-50 disabled:text-gray-500
          dark:border-gray-600 dark:bg-gray-800 dark:text-white
          dark:focus:border-brand-400
          ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </select>
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}
```

## Responsive Design Patterns

### Mobile-First Approach

```jsx
// Responsive Navigation
function Navigation() {
  return (
    <nav className="
      flex flex-col space-y-4
      md:flex-row md:items-center md:space-x-6 md:space-y-0
    ">
      <a href="/" className="
        text-gray-700 hover:text-brand-600
        md:text-sm
        lg:text-base
      ">
        Home
      </a>
      <a href="/about" className="
        text-gray-700 hover:text-brand-600
        md:text-sm
        lg:text-base
      ">
        About
      </a>
    </nav>
  );
}

// Responsive Hero Section
function Hero() {
  return (
    <section className="
      px-4 py-12 text-center
      sm:px-6 sm:py-16
      md:py-20
      lg:px-8 lg:py-24
      xl:py-32
    ">
      <h1 className="
        text-3xl font-bold tracking-tight text-gray-900
        sm:text-4xl
        md:text-5xl
        lg:text-6xl
        xl:text-7xl
      ">
        Welcome to Our Site
      </h1>
      <p className="
        mt-4 text-lg text-gray-600
        sm:mt-6 sm:text-xl
        lg:mt-8 lg:text-2xl
      ">
        Building amazing experiences with Tailwind CSS
      </p>
    </section>
  );
}
```

### Container Queries

```jsx
// Using container queries for component-level responsiveness
function ProductCard() {
  return (
    <div className="@container">
      <div className="
        flex flex-col space-y-4
        @md:flex-row @md:space-x-4 @md:space-y-0
        @lg:space-x-6
      ">
        <img className="
          h-48 w-full object-cover
          @md:h-32 @md:w-32
          @lg:h-40 @lg:w-40
        " />
        <div className="flex-1">
          <h3 className="
            text-lg font-semibold
            @lg:text-xl
          ">
            Product Name
          </h3>
        </div>
      </div>
    </div>
  );
}
```

## Dark Mode Implementation

### CSS Variables Approach

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
    --secondary: 210 40% 96%;
    --secondary-foreground: 222.2 84% 4.9%;
  }
  
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 84% 4.9%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
  }
}
```

### Theme Toggle Component

```jsx
// Theme toggle with smooth transitions
function ThemeToggle() {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };
  
  return (
    <button
      onClick={toggleTheme}
      className="
        rounded-lg p-2 transition-colors duration-200
        hover:bg-gray-100 dark:hover:bg-gray-800
        focus:outline-none focus:ring-2 focus:ring-brand-500
      "
      aria-label="Toggle theme"
    >
      {theme === 'light' ? (
        <MoonIcon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
      ) : (
        <SunIcon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
      )}
    </button>
  );
}
```

## Performance Optimization

### Content Configuration

```javascript
// Optimized content paths for better purging
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    // Include node_modules if using component libraries
    './node_modules/@my-ui-lib/**/*.{js,ts,jsx,tsx}',
  ],
  safelist: [
    // Keep dynamic classes that might be missed by purging
    {
      pattern: /bg-(red|green|blue)-(100|500|900)/,
      variants: ['hover', 'focus'],
    },
  ],
}
```

### Custom Utilities

```css
/* Custom utilities for common patterns */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
  
  .animation-delay-200 {
    animation-delay: 200ms;
  }
  
  .animation-delay-400 {
    animation-delay: 400ms;
  }
  
  .mask-gradient-to-r {
    mask-image: linear-gradient(to right, transparent, black 20%, black 80%, transparent);
  }
}
```

### Component Layer

```css
@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50;
  }
  
  .btn-primary {
    @apply bg-brand-600 text-white hover:bg-brand-700 focus-visible:ring-brand-500;
  }
  
  .card {
    @apply rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900;
  }
  
  .input {
    @apply block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:cursor-not-allowed disabled:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-white;
  }
}
```

## Animation and Motion

### Custom Animations

```javascript
// Advanced animations in Tailwind config
module.exports = {
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-x': 'bounceX 1s infinite',
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        bounceX: {
          '0%, 100%': { transform: 'translateX(-25%)' },
          '50%': { transform: 'translateX(0)' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
}
```

### Staggered Animations

```jsx
// Staggered animation component
function StaggeredList({ items }) {
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div
          key={item.id}
          className={`
            animate-fade-in-up opacity-0
            animation-delay-${index * 100}
          `}
          style={{ animationFillMode: 'forwards' }}
        >
          {item.content}
        </div>
      ))}
    </div>
  );
}
```

## Common Patterns and Solutions

### Truncated Text

```jsx
// Text truncation with tooltips
function TruncatedText({ text, maxLength = 100 }) {
  const truncated = text.length > maxLength;
  const displayText = truncated ? `${text.slice(0, maxLength)}...` : text;
  
  return (
    <span 
      className={`${truncated ? 'cursor-help' : ''}`}
      title={truncated ? text : undefined}
    >
      {displayText}
    </span>
  );
}

// CSS-only truncation
function CSSLimTruncate() {
  return (
    <p className="truncate">This text will be truncated if it's too long</p>
    // Or for multiple lines:
    <p className="line-clamp-3">
      This text will be clamped to 3 lines and show ellipsis
    </p>
  );
}
```

### Aspect Ratio Containers

```jsx
// Responsive aspect ratio containers
function AspectRatioImage({ src, alt, ratio = 'aspect-video' }) {
  return (
    <div className={`relative overflow-hidden rounded-lg ${ratio}`}>
      <img 
        src={src}
        alt={alt}
        className="absolute inset-0 h-full w-full object-cover"
      />
    </div>
  );
}

// Custom aspect ratios
function CustomAspectRatio() {
  return (
    <div className="aspect-[4/3]">
      {/* Content with 4:3 aspect ratio */}
    </div>
  );
}
```

### Focus Management

```jsx
// Accessible focus styles
function FocusExample() {
  return (
    <div className="space-y-4">
      <button className="
        rounded-md bg-brand-600 px-4 py-2 text-white
        focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2
        focus-visible:ring-2 focus-visible:ring-brand-500
      ">
        Accessible Button
      </button>
      
      <input className="
        rounded-md border border-gray-300 px-3 py-2
        focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500
        invalid:border-red-500 invalid:focus:border-red-500 invalid:focus:ring-red-500
      " />
    </div>
  );
}
```

## Plugin Ecosystem

### Typography Plugin

```javascript
// @tailwindcss/typography configuration
module.exports = {
  plugins: [
    require('@tailwindcss/typography')({
      className: 'prose',
    }),
  ],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: 'inherit',
            a: {
              color: 'inherit',
              textDecoration: 'none',
              fontWeight: '500',
            },
            'a:hover': {
              color: '#0ea5e9',
            },
          },
        },
      },
    },
  },
}
```

### Forms Plugin

```javascript
// @tailwindcss/forms configuration
module.exports = {
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class', // or 'base'
    }),
  ],
}
```

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com)
- [Headless UI](https://headlessui.com)
- [Heroicons](https://heroicons.com)
- [Tailwind Play](https://play.tailwindcss.com)
- [Tailwind Community](https://github.com/tailwindlabs/tailwindcss/discussions)

Remember: **Utility-first, mobile-first, performance-first. Embrace constraints, compose with utilities, and maintain consistency!**
