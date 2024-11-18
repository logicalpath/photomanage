#!/bin/bash

usage() {
    echo "Usage: $0 [-d|-x] [-i directory]"
    echo "Remove or display Mac OS resource fork files (._*)"
    echo "  -d    Display files that would be removed"
    echo "  -x    Remove the files"
    echo "  -i    Specify input directory (default: current directory)"
    echo ""
    echo "export COPYFILE_DISABLE=1 to prevent creation of ._ files"
    exit 1
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    usage
fi

# Get directory from -i option if specified
search_dir="."
while getopts ":i:" opt "$@"; do
    case $opt in
        i)
            search_dir="$OPTARG"
            if [ ! -d "$search_dir" ]; then
                echo "Error: Directory '$search_dir' does not exist"
                exit 1
            fi
            break
            ;;
    esac
done

# Reset getopts
OPTIND=1

# Parse remaining command line options
while getopts "dxi:" opt; do
    case $opt in
        d)
            # Display files only
            find "$search_dir" -name '._*' -print
            exit 0
            ;;
        x)
            # Remove the files
            find "$search_dir" -name '._*' -exec rm {} \;
            exit 0
            ;;
        i)
            # Already handled
            ;;
        \?)
            usage
            ;;
    esac
done

# If no action specified (-d or -x), show usage
if [ $OPTIND -eq 1 ]; then
    usage
fi