#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
fi

# Set up virtual environment if it doesn't exist
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Upgrade setuptools to fix build issues with older packages
pip install --upgrade setuptools pip --quiet

# Install psycopg2-binary (avoids needing libpq-dev C headers)
pip install psycopg2-binary --quiet

# Install remaining Python dependencies (psycopg2 already satisfied by binary)
pip install -r requirements.txt --quiet

# Install flake8 for linting
pip install flake8 --quiet

# Create and run Django migrations (uses SQLite by default)
python manage.py makemigrations --no-input --verbosity 0
python manage.py migrate --run-syncdb --no-input --verbosity 0

# Export environment variables for the session
{
  echo "export DJANGO_SETTINGS_MODULE=\"config.settings\""
  echo "export VIRTUAL_ENV=\"$CLAUDE_PROJECT_DIR/.venv\""
  echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\""
} >> "$CLAUDE_ENV_FILE"
