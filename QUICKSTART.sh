#!/bin/bash

echo "🚀 SA Investment Analyzer - Quick Start"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy env file
echo "Creating .env file..."
cp .env.example .env

# Initialize
echo "Initializing system..."
python scripts/init_system.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the dashboard:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"