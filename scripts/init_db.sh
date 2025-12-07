#!/bin/bash
# Database initialization script
# Run this after starting docker-compose to set up the database

echo "Waiting for database to be ready..."
sleep 5

echo "Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo "Database initialization complete!"
echo "You can now access the API at http://localhost:8500"

