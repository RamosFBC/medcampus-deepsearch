#!/bin/bash

# Script to run the MedCampus Streamlit application
echo "Starting MedCampus Streamlit application..."

# Navigate to the project directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Streamlit app
echo "Launching Streamlit app..."
streamlit run src/app.py

# Deactivate virtual environment on exit
deactivate
