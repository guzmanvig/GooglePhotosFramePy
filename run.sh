#!/bin/bash
export XAUTHORITY=$(ls /run/user/1000/.mutter-Xwaylandauth.*)
xhost +local:

# Get the directory of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Change to the directory where the script is located
cd "$SCRIPT_DIR" || exit 1

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
    (cd slideshow-control && npm install && BROWSER=none npm start) &
else
    (cd slideshow-control && BROWSER=none npm start) &
fi

# Run the main.py script
LANG=es_ES.utf8 python3.11 main.py

# Deactivate the virtual environment
deactivate