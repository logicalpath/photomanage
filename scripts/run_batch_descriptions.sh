#!/bin/bash
#
# Start Batch Image Description Processing
#
# This script starts the batch orchestrator with caffeinate to prevent the
# system from sleeping. The process runs in the background and logs to a file.
#
# Usage:
#   ./scripts/run_batch_descriptions.sh [OPTIONS]
#
# Options:
#   --directory PATH      Path to images (default: database/512x512)
#   --batch-size NUM      Images per batch (default: 100)
#   --cooldown SECS       Seconds between batches (default: 30)
#   --model NAME          Model to use: smolvlm or smolvlm2 (default: smolvlm)
#   --max-tokens NUM      Maximum tokens for output (default: 500)
#   --temp VALUE          Temperature 0.0-1.0 (default: 0.0)
#   -h, --help            Show this help message
#
# Examples:
#   ./scripts/run_batch_descriptions.sh
#   ./scripts/run_batch_descriptions.sh --batch-size 50 --cooldown 60
#   ./scripts/run_batch_descriptions.sh --model smolvlm2
#   ./scripts/run_batch_descriptions.sh --max-tokens 300 --temp 0.7
#   ./scripts/run_batch_descriptions.sh --directory /path/to/images --batch-size 200
#

# Default values
DIRECTORY="database/512x512"
BATCH_SIZE="100"
COOLDOWN="30"
MODEL="smolvlm"
MAX_TOKENS="500"
TEMP="0.0"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --directory)
            DIRECTORY="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --cooldown)
            COOLDOWN="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --max-tokens)
            MAX_TOKENS="$2"
            shift 2
            ;;
        --temp)
            TEMP="$2"
            shift 2
            ;;
        -h|--help)
            echo "Start Batch Image Description Processing"
            echo ""
            echo "Usage: ./scripts/run_batch_descriptions.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --directory PATH      Path to images (default: database/512x512)"
            echo "  --batch-size NUM      Images per batch (default: 100)"
            echo "  --cooldown SECS       Seconds between batches (default: 30)"
            echo "  --model NAME          Model to use: smolvlm or smolvlm2 (default: smolvlm)"
            echo "  --max-tokens NUM      Maximum tokens for output (default: 500)"
            echo "  --temp VALUE          Temperature 0.0-1.0 (default: 0.0)"
            echo "  -h, --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./scripts/run_batch_descriptions.sh"
            echo "  ./scripts/run_batch_descriptions.sh --batch-size 50 --cooldown 60"
            echo "  ./scripts/run_batch_descriptions.sh --model smolvlm2"
            echo "  ./scripts/run_batch_descriptions.sh --max-tokens 300 --temp 0.7"
            echo "  ./scripts/run_batch_descriptions.sh --directory /path/to/images --batch-size 200"
            exit 0
            ;;
        *)
            echo "❌ Error: Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

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
echo "Max tokens:     $MAX_TOKENS"
echo "Temperature:    $TEMP"
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
    --max-tokens "$MAX_TOKENS" \
    --temp "$TEMP" \
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
