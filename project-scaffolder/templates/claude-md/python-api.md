# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

## Tech Stack

- **Framework**: FastAPI / Django / Flask
- **Python**: 3.11+
- **Database**: PostgreSQL / SQLite / MongoDB
- **ORM**: SQLAlchemy / Django ORM / Prisma
- **Testing**: pytest + pytest-asyncio
- **Package Manager**: pip / poetry / uv

## Project Structure

```
{{PROJECT_NAME}}/
├── app/
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── config.py         # Configuration management
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── api/              # API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py       # Dependencies (auth, db sessions)
│   │   └── v1/           # API version 1 routes
│   ├── core/             # Core utilities
│   ├── services/         # Business logic
│   └── db/               # Database configuration
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── test_api/         # API tests
│   └── test_services/    # Service tests
├── alembic/              # Database migrations (if using Alembic)
├── pyproject.toml        # Project configuration
└── requirements.txt      # Dependencies
```

## Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# OR with poetry
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

## Commands

```bash
# Development
uvicorn app.main:app --reload          # Start dev server
python -m app.main                      # Alternative start

# Database
alembic upgrade head                    # Run migrations
alembic revision --autogenerate -m "msg" # Create migration

# Quality
ruff check .                            # Lint code
ruff format .                           # Format code
mypy app/                               # Type checking

# Testing
pytest                                  # Run all tests
pytest -v                               # Verbose output
pytest --cov=app                        # With coverage
pytest -k "test_name"                   # Run specific test
```

## Code Patterns

### API Endpoints
- Use dependency injection for database sessions and auth
- Return Pydantic models for type-safe responses
- Use proper HTTP status codes
- Include OpenAPI documentation

### Database Models
- Use UUID primary keys for public-facing IDs
- Include `created_at` and `updated_at` timestamps
- Define relationships explicitly

### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Create custom exception classes for business logic errors
- Return consistent error response format

### Type Hints
- Use type hints on ALL function signatures
- Use `Optional` explicitly, avoid implicit None
- Define complex types in `schemas/` directory

## Verification Checklist

Before committing:
1. `ruff check .` passes (no lint errors)
2. `mypy app/` passes (no type errors)
3. `pytest` passes (all tests green)
4. API documentation is updated

## File Boundaries

- **Safe to edit**: `/app/`, `/tests/`
- **Config files**: `/pyproject.toml`, `/alembic.ini`
- **Never touch**: `/venv/`, `/__pycache__/`, `/.git/`

## Common Tasks

### Adding a New Endpoint
1. Create route handler in `app/api/v1/`
2. Define request/response schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add tests in `tests/test_api/`
5. Register router in `app/api/v1/__init__.py`

### Adding a Database Model
1. Create model in `app/models/`
2. Create Alembic migration: `alembic revision --autogenerate -m "add model"`
3. Run migration: `alembic upgrade head`
4. Create Pydantic schemas for API

### Adding a Background Task
1. Define task function in `app/tasks/`
2. Configure task queue (Celery/ARQ)
3. Add task trigger to appropriate endpoint
