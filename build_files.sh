#!/bin/bash

# Build script for Vercel deployment
echo "BUILD START"

# Install dependencies
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

# Make sure staticfiles_build directory exists
mkdir -p staticfiles_build/static

# Collect static files
python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END" 