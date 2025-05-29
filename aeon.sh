# aeon.sh
#!/bin/bash

# --- Configuration ---
# Path to your virtual environment directory
VENV_DIR="./.venv"

# Name of your Python script and its directory (as a package)
PYTHON_SCRIPT_DIR="core"
PYTHON_MAIN_MODULE="aeon"

# --- Script Logic ---

# Clear screen for interactive mode
clear
echo -e "\033[1;93m[BOOT]\033[0m Booting AEON"
echo -e "\033[1;93m[BOOT]\033[0m Activating virtual environment..."

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

echo -e "\033[1;93m[BOOT]\033[0m Running AEON..."

# Add the current directory to PYTHONPATH so Python can find the 'core' package
export PYTHONPATH=$(pwd):$PYTHONPATH

python -m "$PYTHON_SCRIPT_DIR.$PYTHON_MAIN_MODULE"

# Deactivate the virtual environment when the Python script finishes
deactivate

echo -e "\033[1;93m[BOOT]\033[0m AEON Ended"
echo -e "\033[1;93m[BOOT]\033[0m Virtual environment deactivated."
echo -e "\033[1;31m[WRN]\033[0m Nothing will be remembered."