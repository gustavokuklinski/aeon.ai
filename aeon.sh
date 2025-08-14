#!/bin/bash

# --- Configuration ---
# Path to your virtual environment directory
VENV_DIR="./.venv"

# Name of your Python script and its directory (as a package) for terminal mode
PYTHON_SCRIPT_DIR="core"
PYTHON_MAIN_MODULE="aeon"

# Path to the Flask app for web mode
FLASK_APP_PATH="web/aeon-web.py"

# --- Script Logic ---

# Clear screen for interactive mode
clear
echo -e "\033[1;93m[BOOT]\033[0m Booting AEON"
echo -e "\033[1;93m[BOOT]\033[0m Activating virtual environment..."

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at '$VENV_DIR'."
    echo "Please create it first using: python3 -m venv .venv"
    echo "Then install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Add the current directory to PYTHONPATH so Python can find the 'core' package
export PYTHONPATH=$(pwd):$PYTHONPATH

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
            echo "Error: Python main module '$PYTHON_SCRIPT_DIR/$PYTHON_MAIN_MODULE.py' not found."
            echo "Make sure the 'core' directory and 'aeon.py' exist within it."
            deactivate
            exit 1
        fi
        echo -e "\033[1;93m[BOOT]\033[0m Running AEON in Terminal mode..."
        python -m "$PYTHON_SCRIPT_DIR.$PYTHON_MAIN_MODULE"
        ;;
    2)
        # Run in web mode
        if [ ! -f "$FLASK_APP_PATH" ]; then
            echo "Error: Flask app file '$FLASK_APP_PATH' not found."
            echo "Make sure the 'web' directory and 'aeon-web.py' exist within it."
            deactivate
            exit 1
        fi
        echo -e "\033[1;93m[BOOT]\033[0m Running AEON in Web mode..."
        echo -e "\033[1;93m[BOOT]\033[0m Access the web interface at: http://127.0.0.1:4303"
        # Run Flask app with debug mode (for development)
        python "$FLASK_APP_PATH"
        ;;
    3)
        echo -e "\033[1;93m[BOOT]\033[0m Exiting AEON. Goodbye!"
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, or 3."
        ;;
esac

# Deactivate the virtual environment when the script finishes
deactivate

echo -e "\033[1;93m[BOOT]\033[0m Virtual environment deactivated."
if [ "$choice" != "3" ]; then
    echo -e "\033[1;31m[WRN]\033[0m Nothing will be remembered (conversation state is stateless)."
fi
echo -e "\033[1;93m[BOOT]\033[0m AEON Ended."