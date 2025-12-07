# Alembic Migrations

This directory contains database migration scripts managed by Alembic.

## Creating a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration file
alembic revision -m "description of changes"
```

## Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show migration history
alembic history
```

## Inside Docker

```bash
# Run migrations inside the API container
docker-compose exec api alembic upgrade head
```

