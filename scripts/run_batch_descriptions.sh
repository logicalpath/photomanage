#!/bin/bash
#
# Start Batch Image Description Processing
#
# This script starts the batch orchestrator with caffeinate to prevent the
# system from sleeping. The process runs in the background and logs to a file.
#
# Usage:
#   ./scripts/run_batch_descriptions.sh [directory] [batch_size] [cooldown] [model]
#
# Examples:
#   ./scripts/run_batch_descriptions.sh
#   ./scripts/run_batch_descriptions.sh database/512x512 50 60
#   ./scripts/run_batch_descriptions.sh database/512x512 100 30 smolvlm2
#

# Default values
DIRECTORY="${1:-database/512x512}"
BATCH_SIZE="${2:-100}"
COOLDOWN="${3:-30}"
MODEL="${4:-smolvlm}"

# PID file location
PID_FILE="batch_orchestrator.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Error: Batch orchestrator is already running (PID: $PID)"
        echo "   Use './scripts/stop_batch_descriptions.sh' to stop it first"
        exit 1
    else
        echo "⚠️  Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Validate directory
if [ ! -d "$DIRECTORY" ]; then
    echo "❌ Error: Directory not found: $DIRECTORY"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Display configuration
echo "="
echo "Starting Batch Image Description Processing"
echo "="
echo "Directory:      $DIRECTORY"
echo "Batch size:     $BATCH_SIZE images per batch"
echo "Cooldown:       ${COOLDOWN}s between batches"
echo "Model:          $MODEL"
echo ""

# Count files
echo "Counting files..."
FILE_COUNT=$(find "$DIRECTORY" -type f ! -name '.*' ! -name '.DS_Store' | wc -l | tr -d ' ')
echo "Total files:    $FILE_COUNT"
echo ""

# Start the orchestrator with caffeinate in background
# caffeinate prevents sleep even with lid closed (when plugged in)
# nohup ensures it continues after shell exits
echo "Starting orchestrator..."
nohup caffeinate -i python3 src/batch_orchestrator.py \
    "$DIRECTORY" \
    --batch-size "$BATCH_SIZE" \
    --cooldown "$COOLDOWN" \
    --model "$MODEL" \
    > logs/orchestrator_console.log 2>&1 &

# Save the PID
ORCHESTRATOR_PID=$!
echo $ORCHESTRATOR_PID > "$PID_FILE"

# Wait a moment to check if it started successfully
sleep 2

if ps -p "$ORCHESTRATOR_PID" > /dev/null 2>&1; then
    echo "✅ Batch orchestrator started successfully!"
    echo ""
    echo "Process ID:     $ORCHESTRATOR_PID"
    echo "PID file:       $PID_FILE"
    echo "Console log:    logs/orchestrator_console.log"
    echo ""
    echo "Monitor progress:"
    echo "  python src/check_progress.py"
    echo "  python src/progress_summary.py"
    echo "  tail -f logs/orchestrator_console.log"
    echo ""
    echo "Watch dashboard (auto-refresh every 30s):"
    echo "  watch -n 30 'python src/check_progress.py'"
    echo ""
    echo "Stop processing:"
    echo "  ./scripts/stop_batch_descriptions.sh"
    echo ""
else
    echo "❌ Error: Failed to start orchestrator"
    echo "Check logs/orchestrator_console.log for details"
    rm "$PID_FILE"
    exit 1
fi
