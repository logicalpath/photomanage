#!/bin/bash
#
# Stop Batch Image Description Processing
#
# This script safely stops the batch orchestrator using a flag file approach.
# The current image will complete, results will be saved, then the process exits.
#
# Usage:
#   ./scripts/stop_batch_descriptions.sh
#

PID_FILE="batch_orchestrator.pid"
STOP_FLAG=".stop_requested"

# Cleanup function to remove stop flag
cleanup() {
    rm -f "$STOP_FLAG"
}

# Always clean up the stop flag on exit
trap cleanup EXIT

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

# Create stop flag file - the Python script checks for this between images
echo "Creating stop flag..."
touch "$STOP_FLAG"

# Verify PID belongs to our orchestrator before sending signals
PROC_CMD=$(ps -p "$PID" -o args= 2>/dev/null)
if [[ "$PROC_CMD" != *"batch_orchestrator"* ]]; then
    echo "❌ Error: PID $PID does not match batch orchestrator process"
    echo "   Found: $PROC_CMD"
    rm -f "$PID_FILE"
    exit 1
fi

# Send SIGINT to orchestrator so it doesn't start new batches
echo "Signaling orchestrator to stop..."
kill -INT "$PID" 2>/dev/null

echo ""
echo "Waiting for current image to complete and save..."
echo "(This should take less than 30 seconds)"
echo ""

# Wait for process to stop (up to 5 minutes, but should be much faster)
WAIT_TIME=0
MAX_WAIT=300

while ps -p "$PID" > /dev/null 2>&1; do
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo ""
        echo "⚠️  Process did not stop within ${MAX_WAIT}s"
        echo "Forcing stop..."
        # Re-verify PID before SIGKILL
        PROC_CMD=$(ps -p "$PID" -o args= 2>/dev/null)
        if [[ "$PROC_CMD" == *"batch_orchestrator"* ]]; then
            kill -TERM "$PID" 2>/dev/null
            sleep 5
            kill -9 "$PID" 2>/dev/null
        else
            echo "⚠️  Process changed, skipping forced kill"
        fi
        sleep 2
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
    rm -f "$PID_FILE"

    # Show final progress
    echo ""
    echo "Checking final progress..."
    python src/check_progress.py 2>/dev/null || echo "Unable to check progress"

    # Check for any missing descriptions
    echo ""
    python scripts/find_missing_descriptions.py 2>/dev/null || true
else
    echo "❌ Error: Unable to stop process"
    exit 1
fi
