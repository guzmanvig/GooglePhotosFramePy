#!/bin/bash

# Check if the venv directory exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv venv

    echo "Installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# Activate the virtual environment
source venv/bin/activate

# Start the React app in the background
if [ ! -d "slideshow-control/node_modules" ]; then
    (cd slideshow-control && npm install && npm start) &
else
    (cd slideshow-control && npm start) &
fi

# Run the main.py script
python3.11 main.py

# Deactivate the virtual environment
deactivate