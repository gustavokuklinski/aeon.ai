#!/bin/bash

# --- Configuration ---
# Path to your virtual environment directory
VENV_DIR="./.venv"

# Name of your Python script and its directory (as a package) for terminal mode
PYTHON_SCRIPT_DIR="core"
PYTHON_MAIN_MODULE="aeon"

# Path to the Flask app for web mode
FLASK_APP_PATH="core/web.py" # Corrected path to match recent conventions

# Path to requirements.txt
REQUIREMENTS_FILE="requirements.txt"

# Path to config.json
CONFIG_FILE="config.json"

# --- Script Logic ---

# Clear screen for interactive mode
clear
echo -e "\033[1;93m[BOOT]\033[0m Booting AEON"
echo -e "\033[1;93m[BOOT]\033[0m Checking virtual environment..."

# Check if the virtual environment exists. If not, create and install dependencies.
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\033[91m[ERROR]\033[0m Virtual environment not found at '$VENV_DIR'."
    echo -e "\033[1;34m[INFO]\033[0m Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || { echo -e "\033[91m[ERROR]\033[0m Failed to create virtual environment. Aborting."; exit 1; }
    echo -e "\033[1;32m[OK]\033[0m Virtual environment created."
    
    source "$VENV_DIR/bin/activate"
    
    echo -e "\033[1;34m[INFO]\033[0m Installing dependencies from 'requirements.txt'..."
    pip install -r "$REQUIREMENTS_FILE" || { echo -e "\033[91m[ERROR]\033[0m Failed to install dependencies. Aborting."; deactivate; exit 1; }
    echo -e "\033[1;32m[OK]\033[0m Dependencies installed successfully."
else
    echo -e "\033[1;32m[OK]\033[0m Virtual environment found. Activating..."
    source "$VENV_DIR/bin/activate"
fi

# Add the current directory to PYTHONPATH so Python can find the 'core' package
export PYTHONPATH=$(pwd):$PYTHONPATH

# --- Pre-flight Checks ---

echo -e "\n\033[1;93m[BOOT]\033[0m Running pre-flight checks..."

# 1. Verify 'jq' installation
echo -e "\033[1;34m[INFO]\033[0m Checking for 'jq' (JSON processor)..."
if ! command -v jq &> /dev/null; then
    echo -e "\033[91m[ERROR]\033[0m The 'jq' tool is not installed or not in your system's PATH."
    echo -e "\033[91m[ERROR]\033[0m 'jq' is required to parse the config.json file."
    echo -e "\033[91m[ERROR]\033[0m Please install it using your system's package manager (e.g., 'sudo apt-get install jq' or 'brew install jq')."
    deactivate
    exit 1
fi
echo -e "\033[1;32m[OK]\033[0m 'jq' is installed."

# 2. Verify Python requirements for Hugging Face (a lighter check)
echo -e "\033[1;34m[INFO]\033[0m Checking for Hugging Face libraries..."
python -c "import transformers, torch, sentence_transformers, accelerate, diffusers, bitsandbytes" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "\033[91m[ERROR]\033[0m Hugging Face dependencies are not installed."
    echo -e "\033[91m[ERROR]\033[0m Please run: \033[36mpip install -r $REQUIREMENTS_FILE\033[0m"
    deactivate
    exit 1
fi
echo -e "\033[1;32m[OK]\033[0m Hugging Face libraries found."


echo -e "\n\033[1;93m[BOOT]\033[0m All pre-flight checks passed. Launching AEON..."

# --- Main Menu and Execution ---

echo -e
echo -e "\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m"
echo -e "\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m"
echo -e "\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m"
echo -e "\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m"
echo -e "\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m"
echo -e "\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m"
echo -e
echo -e "-------------------------------------"
echo -e "How do you wish to run?"
echo -e "\033[91m[1]\033[0m Terminal"
echo -e "\033[91m[2]\033[0m Web Chat"
echo -e "\033[91m[3]\033[0m Exit"
read -e -p $'\n\033[1;36m[AEON_PROMPT]\033[0m \033[1;92m>> \033[0m' choice
echo -e
case $choice in
    1)
        # Run in terminal mode
        if [ ! -f "$PYTHON_SCRIPT_DIR/$PYTHON_MAIN_MODULE.py" ]; then
            echo -e "\033[91m[ERROR]\033[0m Python main module '$PYTHON_SCRIPT_DIR/$PYTHON_MAIN_MODULE.py' not found."
            echo -e "\033[91m[ERROR]\033[0m Make sure the 'core' directory and 'aeon.py' exist within it."
            deactivate
            exit 1
        fi
        echo -e "\033[1;93m[BOOT]\033[0m Running AEON in Terminal mode..."
        python -m "$PYTHON_SCRIPT_DIR.$PYTHON_MAIN_MODULE"
        ;;
    2)
        # Run in web mode
        if [ ! -f "$FLASK_APP_PATH" ]; then
            echo -e "\033[91m[ERROR]\033[0m Flask app file '$FLASK_APP_PATH' not found."
            echo -e "\033[91m[ERROR]\033[0m Make sure the 'web' directory and 'app.py' exist within it."
            deactivate
            exit 1
        fi
        echo -e "\033[1;93m[BOOT]\033[0m Running AEON in Web mode..."
        echo -e "\033[1;93m[BOOT]\033[0m Access the web interface at: http://127.0.0.1:4303"
        python "$FLASK_APP_PATH"
        ;;
    3)
        echo -e "\033[1;93m[BOOT]\033[0m Exiting AEON. Goodbye!"
        ;;
    *)
        echo -e "\033[91m[ERROR]\033[0m Invalid choice. Please enter 1, 2, or 3."
        ;;
esac

# Deactivate the virtual environment when the script finishes
deactivate

echo -e "\033[1;93m[BOOT]\033[0m Virtual environment deactivated."
if [ "$choice" != "3" ]; then
    echo -e "\033[1;31m[WRN]\033[0m Nothing will be remembered (conversation state is stateless)."
fi
echo -e "\033[1;93m[BOOT]\033[0m AEON Ended."