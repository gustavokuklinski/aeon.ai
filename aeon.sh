#!/bin/bash

# --- Configuration ---
# Path to your virtual environment directory
VENV_DIR="./.venv"

# Name of your Python script and its directory (as a package)
PYTHON_SCRIPT_DIR="core"
PYTHON_MAIN_MODULE="aeon"

# --- Script Logic ---

# Determine if we are in quick query mode
IS_QUICK_QUERY=false
QUERY_ARG=""
if [[ "$1" == "-q" ]]; then
    IS_QUICK_QUERY=true
    if [ -n "$2" ]; then
        QUERY_ARG="$2"
        # Shift arguments so python can receive only the query
        shift 2
    else
        echo "Error: -q option requires a query string."
        exit 1
    fi
fi

# Clear screen only for interactive mode
if [ "$IS_QUICK_QUERY" = false ]; then
    clear
    echo -e "\033[1;93m[BOOT]\033[0m Booting AEON"
    echo -e "\033[1;93m[BOOT]\033[0m Activating virtual environment..."
fi

# Check if the virtual environment exists (critical error, always show)
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at '$VENV_DIR'."
    echo "Please create it first using: python3 -m venv venv"
    echo "Then install dependencies: pip install -U langchain langchain-community langchain-ollama chromadb unstructured markdown Pillow requests svgwrite"
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Check if the main Python module exists (critical error, always show)
if [ ! -f "$PYTHON_SCRIPT_DIR/$PYTHON_MAIN_MODULE.py" ]; then
    echo "Error: Python main module '$PYTHON_SCRIPT_DIR/$PYTHON_MAIN_MODULE.py' not found."
    echo "Make sure the 'core' directory and 'aeon.py' exist within it."
    deactivate # Deactivate venv before exiting
    exit 1
fi

if [ "$IS_QUICK_QUERY" = false ]; then
    echo -e "\033[1;93m[BOOT]\033[0m Running AEON..."
fi

# Add the current directory to PYTHONPATH so Python can find the 'core' package
export PYTHONPATH=$(pwd):$PYTHONPATH

PYTHON_ARGS=""
if [ "$IS_QUICK_QUERY" = true ]; then
    # In quick query mode, pass the query and the hide-boot-messages flag
    PYTHON_ARGS="--query \"$QUERY_ARG\" --hide-boot-messages"
else
    # In interactive mode, no extra arguments needed for Python beyond what it expects
    PYTHON_ARGS=""
fi

python -m "$PYTHON_SCRIPT_DIR.$PYTHON_MAIN_MODULE" $PYTHON_ARGS

# Deactivate the virtual environment when the Python script finishes
deactivate

# Only show final shell script messages if not in quick query mode
if [ "$IS_QUICK_QUERY" = false ]; then
    echo -e "\033[1;93m[BOOT]\033[0m AEON Ended"
    echo -e "\033[1;93m[BOOT]\033[0m Virtual environment deactivated."
    echo -e "\033[1;31m[WRN]\033[0m Nothing will be remembered."
fi
