#!/bin/bash

# Vector My Shit - Startup Script

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Start the server
echo "Starting Vector My Shit server..."
echo "Server will be available at http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python3 server.py

