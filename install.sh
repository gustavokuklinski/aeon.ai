#!/bin/bash

echo "--- Installing Python dependencies from requirements.txt ---"

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip is not installed. Please install pip first."
    echo "For example, on Debian/Ubuntu: sudo apt install python3-pip"
    echo "On macOS with Homebrew: brew install python"
    exit 1
fi

# Check if python3 is installed and available for venv
if ! command -v python3 &> /dev/null
then
    echo "python3 is not installed. Please install python3 to create a virtual environment."
    echo "For example, on Debian/Ubuntu: sudo apt install python3"
    echo "On macOS with Homebrew: brew install python"
    exit 1
fi

# Create a virtual environment
echo "--- Creating virtual environment '.venv' ---"
python3 -m venv .venv

if [ $? -ne 0 ]; then
    echo "--- Error: Failed to create virtual environment. ---"
    exit 1
fi

# Activate the virtual environment
echo "--- Activating virtual environment ---"
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo "--- Error: Failed to activate virtual environment. ---"
    exit 1
fi

# Install dependencies within the virtual environment
echo "--- Installing dependencies into the virtual environment ---"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "--- All Python dependencies installed successfully in the virtual environment! ---"
    echo "--- To deactivate the virtual environment, simply type 'deactivate' ---"
else
    echo "--- Error: Failed to install some Python dependencies. Please check the output above. ---"
    # Deactivate the environment on error before exiting
    deactivate
    exit 1
fi
