#!/bin/bash

# Build script for Vercel deployment
echo "BUILD START"

# Install dependencies
python3.9 -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END" 