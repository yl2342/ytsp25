#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Initialize migrations if directory doesn't exist
if [ ! -d "migrations" ]; then
  echo "Migrations directory not found, initializing..."
  python -m flask db init
fi

# Run database migrations
python -m flask db migrate -m "Initial migration from Render deployment"
python -m flask db upgrade 