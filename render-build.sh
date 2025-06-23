#!/bin/bash
# This script runs on Render.com during deployment

# Exit on error
set -o errexit

# Create virtual env if it doesn't exist
if [ ! -d .venv ]; then
    python -m venv .venv
fi

# Install Python dependencies
.venv/bin/pip install -r requirements.txt

# Run database migrations
.venv/bin/python -m flask db upgrade

# Run any setup scripts needed
echo "Deployment setup complete"
