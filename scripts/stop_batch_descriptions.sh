#!/bin/bash
#
# Stop Batch Image Description Processing
#
# This script safely stops the batch orchestrator. The current batch will
# complete before stopping, ensuring no corruption of the progress file.
#
# Usage:
#   ./scripts/stop_batch_descriptions.sh
#

PID_FILE="batch_orchestrator.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Error: No batch orchestrator appears to be running"
    echo "   (PID file not found: $PID_FILE)"
    exit 1
fi

# Read the PID
PID=$(cat "$PID_FILE")

# Check if process is actually running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  Process not running (stale PID file)"
    rm "$PID_FILE"
    exit 0
fi

echo "Stopping batch orchestrator (PID: $PID)..."
echo ""
echo "Sending interrupt signal..."
echo "The current batch will complete before stopping."
echo ""

# Send SIGINT (same as Ctrl+C) for graceful shutdown
kill -INT "$PID"

# Wait for process to stop (up to 60 seconds)
WAIT_TIME=0
MAX_WAIT=60

while ps -p "$PID" > /dev/null 2>&1; do
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo ""
        echo "⚠️  Process did not stop gracefully within ${MAX_WAIT}s"
        echo "Sending TERM signal..."
        kill -TERM "$PID"
        sleep 5

        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  Process still running. Forcing stop..."
            kill -9 "$PID"
            sleep 2
        fi
        break
    fi

    echo -n "."
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

echo ""

# Verify process stopped
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Batch orchestrator stopped successfully"
    rm "$PID_FILE"

    # Show final progress
    echo ""
    echo "Checking final progress..."
    python src/check_progress.py 2>/dev/null || echo "Unable to check progress"
else
    echo "❌ Error: Unable to stop process"
    exit 1
fi
