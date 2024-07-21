#!/bin/bash

# Check if the venv directory exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.12 -m venv venv

    echo "Installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# Activate the virtual environment
source venv/bin/activate

# Run the main.py script
python3.12 main.py

# Deactivate the virtual environment
deactivate
