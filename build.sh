#!/usr/bin/env bash
# exit on error
set -o errexit

# Print Python version for debugging
python --version

# Enter BBM directory
cd BBM

# Install dependencies
pip install -r requirements.txt

# Make the database directory persistent
mkdir -p /tmp/db

# Copy the database if it exists
if [ -f db.sqlite3 ]; then
    cp db.sqlite3 /tmp/db/db.sqlite3
fi

# Do not run migrations or collectstatic here - we'll do that in the start command
echo "Build completed successfully"
