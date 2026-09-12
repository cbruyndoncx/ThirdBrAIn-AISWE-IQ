# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

## Tech Stack

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite / Next.js / Create React App
- **Styling**: Tailwind CSS / CSS Modules / Styled Components
- **State Management**: React Query / Zustand / Redux Toolkit
- **Testing**: Vitest / Jest + React Testing Library

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Page-level components (routes)
├── hooks/          # Custom React hooks
├── utils/          # Utility functions
├── types/          # TypeScript type definitions
├── services/       # API clients and external services
├── stores/         # State management stores
└── assets/         # Static assets (images, fonts)
```

## Commands

```bash
# Development
npm run dev         # Start development server
npm run build       # Build for production
npm run preview     # Preview production build

# Quality
npm run typecheck   # Run TypeScript compiler
npm run lint        # Run ESLint
npm run lint:fix    # Fix auto-fixable lint issues
npm run format      # Run Prettier

# Testing
npm test            # Run tests
npm run test:watch  # Run tests in watch mode
npm run test:cov    # Run tests with coverage
```

## Code Patterns

### Component Structure
- Use function components with hooks
- Colocate component files: `ComponentName/index.tsx`, `ComponentName.test.tsx`, `ComponentName.module.css`
- Export components as named exports

### TypeScript
- Prefer `interface` for object shapes, `type` for unions/intersections
- Use strict mode (`strict: true` in tsconfig)
- Define prop types inline or in adjacent `.types.ts` files

### Data Fetching
- Use React Query for server state
- Handle loading, error, and success states explicitly
- Implement optimistic updates where appropriate

## Verification Checklist

Before committing, ensure:
1. `npm run typecheck` passes with no errors
2. `npm run lint` reports no issues
3. `npm test` passes all tests
4. Manual verification in browser if UI changes

## File Boundaries

- **Safe to edit**: `/src/`, `/tests/`, `/public/`
- **Config files**: Edit carefully, understand implications
- **Never touch**: `/node_modules/`, `/.git/`, `/dist/`

## Common Tasks

### Adding a New Component
1. Create folder in `/src/components/ComponentName/`
2. Add `index.tsx` with component implementation
3. Add `ComponentName.test.tsx` with basic tests
4. Export from `/src/components/index.ts`

### Adding a New Page/Route
1. Create page component in `/src/pages/`
2. Add route configuration
3. Update navigation if needed
4. Add page-level tests

### Adding an API Integration
1. Create service in `/src/services/`
2. Define TypeScript types for request/response
3. Create React Query hook in `/src/hooks/`
4. Handle loading and error states in consuming components
