@echo off

REM Check if the venv directory exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv

    echo Installing requirements...
    call venv\Scripts\activate
    pip install -r requirements.txt
    call venv\Scripts\deactivate
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the main.py script
REM Using absolute path so it can be run throw window task scheduler
python C:\Users\Guz\Desktop\google_photos_frame\main.py

REM Deactivate the virtual environment
deactivate