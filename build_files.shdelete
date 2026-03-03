#!/bin/bash

# Build script for Vercel deployment
# This script runs during the build process on Vercel

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations (only if using SQLite or if database is accessible)
# For PostgreSQL on Vercel, migrations should be run separately
echo "Running migrations..."
python manage.py migrate --noinput || echo "Migration failed - may need to run manually"

echo "Build process completed!"
