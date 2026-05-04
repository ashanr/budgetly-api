# Budgetly AI Assistant API

A production-ready FastAPI application providing AI-powered personal finance management.

## Features

- **Authentication**: JWT-based auth with access/refresh tokens
- **AI Analysis**: Spending analysis, natural language queries, daily digest
- **Reports**: Summary, monthly, category, and forecast reports
- **Export & Backup**: CSV, JSON export with backup/restore
- **Budget Tracking**: Budget health monitoring with alerts

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Run the API
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest tests/ -v
```

## Docker

```bash
docker-compose up --build
```

## Project Structure

- `app/` - Application source code
  - `api/` - Route handlers
  - `core/` - Config, security, logging, exceptions
  - `models/` - SQLAlchemy ORM models
  - `schemas/` - Pydantic schemas
  - `services/` - Business logic
  - `repositories/` - Database access layer
  - `utils/` - Utility functions
- `tests/` - Test suite
- `alembic/` - Database migrations
