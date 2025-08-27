#!/bin/bash

# Fix Alembic Migrations Script
# Run this if you encounter migration issues

set -e

echo "🔧 Fixing Alembic migrations..."

# Navigate to project directory
cd /var/www/tinderlike

# Activate virtual environment
source venv/bin/activate

# Remove existing database and migration files
echo "🗑️ Cleaning up existing database and migrations..."
rm -f tinderlike.db
rm -rf alembic/versions/*

# Create fresh initial migration
echo "📝 Creating fresh initial migration..."
alembic revision --autogenerate -m "Initial migration for SQLite"

# Run the migration
echo "🚀 Running migration..."
alembic upgrade head

echo "✅ Migrations fixed successfully!"
echo "📋 Database is now ready for seeding."
