#!/bin/bash

# Kill all Python and Node processes
pkill -f "python"
pkill -f "node"

# Get wake-up timestamp for 9 AM tomorrow
WAKE_TIME=$(date -d '09:00 tomorrow' +%s)

# Suspend the system and set wake-up time
sudo rtcwake -m mem -t $WAKE_TIME