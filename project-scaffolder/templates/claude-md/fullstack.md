# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│    Database     │
│  (React/Vue)    │     │  (API Server)   │     │  (PostgreSQL)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: React / Vue / Svelte
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query + Zustand

### Backend
- **Framework**: FastAPI / Express / NestJS
- **Language**: Python / TypeScript
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy / Prisma

## Project Structure

```
{{PROJECT_NAME}}/
├── frontend/              # Frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/     # API client
│   │   └── types/        # Shared types
│   ├── package.json
│   └── tsconfig.json
├── backend/               # Backend application
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   └── requirements.txt
├── shared/                # Shared types/contracts (optional)
│   └── types/
├── docker-compose.yml     # Local development setup
└── README.md
```

## Commands

### Frontend
```bash
cd frontend
npm run dev       # Start dev server (port 3000)
npm run build     # Build for production
npm run test      # Run tests
npm run typecheck # Check TypeScript
```

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000  # Start API server
pytest                                       # Run tests
ruff check . && mypy app/                   # Lint + typecheck
```

### Full Stack (via Docker)
```bash
docker-compose up        # Start all services
docker-compose up -d     # Start in background
docker-compose down      # Stop all services
docker-compose logs -f   # View logs
```

## Development Workflow

### When Working on Frontend
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Access app at http://localhost:3000
4. API available at http://localhost:8000

### When Working on Backend
1. Start database: `docker-compose up db`
2. Start backend: `cd backend && uvicorn app.main:app --reload`
3. Use API docs at http://localhost:8000/docs

## Verification Checklist

### Frontend Changes
1. `npm run typecheck` passes
2. `npm run lint` passes
3. `npm test` passes
4. Manual browser testing

### Backend Changes
1. `ruff check .` passes
2. `mypy app/` passes
3. `pytest` passes
4. API documentation updated

### Full Stack Changes
1. All frontend checks pass
2. All backend checks pass
3. Integration tests pass
4. `docker-compose up` works

## API Contract

API endpoints are documented at `http://localhost:8000/docs` (Swagger UI).

When changing API contracts:
1. Update backend schemas first
2. Update frontend API client types
3. Update frontend consuming components
4. Run integration tests

## File Boundaries

- **Frontend safe**: `/frontend/src/`
- **Backend safe**: `/backend/app/`, `/backend/tests/`
- **Shared safe**: `/shared/`
- **Never touch**: `*/node_modules/`, `*/__pycache__/`, `/.git/`
