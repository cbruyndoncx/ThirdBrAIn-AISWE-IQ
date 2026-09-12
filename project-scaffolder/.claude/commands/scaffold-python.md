# Quick Python API Project Scaffold

Quickly scaffold a new Python API project (FastAPI) with Claude Code configuration.

## Arguments

$ARGUMENTS should contain: `<project-name> [target-directory]`

## Process

### 1. Create Project Structure

```bash
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME
```

Create the following structure:
```
$PROJECT_NAME/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── pyproject.toml
├── requirements.txt
└── .env.example
```

### 2. Create pyproject.toml

```toml
[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "A FastAPI application"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.22.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "C4"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### 3. Create Basic App Files

**app/main.py**:
```python
from fastapi import FastAPI

app = FastAPI(title="$PROJECT_NAME")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**app/config.py**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### 5. Generate CLAUDE.md

Use the `python-api.md` template from `/templates/claude-md/`. Customize for:
- Actual project name
- Detected package manager (pip/poetry/uv)
- Adjusted commands

### 6. Create Slash Commands

Create `.claude/commands/` with:
- **add-endpoint.md** - Add a new API endpoint
- **add-model.md** - Add a new database model
- **test.md** - Run tests with coverage

### 7. Verify

1. Run `ruff check .`
2. Run `mypy app/`
3. Start server: `uvicorn app.main:app --reload`
4. Check http://localhost:8000/docs

### Output

Summarize what was created and provide next steps.
