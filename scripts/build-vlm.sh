#!/bin/bash

# This script automates the creation of a custom Ollama model
# from a local GGUF file using a dynamically generated Modelfile.

# --- Configuration ---

# REQUIRED: Set the path to your GGUF file.
# This path should be correct relative to where you run this script,
# or provide an absolute path (e.g., "/home/user/my_models/my-custom-model.gguf").
GGUF_FILE="aeon-SmolVLM-256M.gguf" # <--- IMPORTANT: Update this path!

# REQUIRED: Set the desired name for your new Ollama model.
MODEL_NAME="aeonVLM" # <--- IMPORTANT: Customize this name!

# Optional: Name for the temporary Modelfile
# This file will be created and then deleted by the script.
MODELFILE_NAME="custom-vlm.modelfile"

# --- Functions ---

# Function to print messages in green
print_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

# Function to print warnings in yellow
print_warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

# Function to print errors in red
print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# --- Main Script ---

print_info "Starting Ollama model creation script..."

# 1. Validate GGUF file existence
if [ ! -f "$GGUF_FILE" ]; then
    print_error "GGUF file not found: '$GGUF_FILE'"
    print_error "Please ensure the GGUF file exists at the specified path and update the 'GGUF_FILE' variable in this script."
    exit 1
fi

print_info "Using GGUF file: '$GGUF_FILE'"

# 2. Define the Modelfile content
# Customize the SYSTEM prompt and PARAMETER values below to define your model's behavior.
read -r -d '' MODELFILE_CONTENT << EOM
FROM $GGUF_FILE

SYSTEM """
<|im_start|>system
When presented with images, focus on describing visual details, relationships between objects, and inferring context or actions within the scene. If asked about an image, analyze its content and provide a relevant, factual description.
<|im_end|>
"""

PARAMETER temperature 0.5

# PARAMETER top_k 40
# PARAMETER top_p 0.9
# PARAMETER num_ctx 4096
# PARAMETER repeat_penalty 1.1
# PARAMETER stop "[/INST]"
# PARAMETER stop "### Instruction:"
# PARAMETER stop "### Response:"
# PARAMETER stop "<|im_end|>"

EOM

# 3. Create the temporary Modelfile
print_info "Creating temporary Modelfile: '$MODELFILE_NAME'"
echo "$MODELFILE_CONTENT" > "$MODELFILE_NAME"

# 4. Create the Ollama model using the Modelfile
print_info "Attempting to create Ollama model '$MODEL_NAME'..."
# The 'ollama create' command copies the GGUF file into Ollama's internal storage
# and applies the Modelfile configurations.
ollama create "$MODEL_NAME" -f "$MODELFILE_NAME"

# Check the exit status of the ollama create command
if [ $? -eq 0 ]; then
    print_info "Successfully created Ollama model: '$MODEL_NAME'"
    print_info "You can now run it using: ollama run $MODEL_NAME"
    print_info "To use it in your Python script, update 'llm_config.model' in your config.json to '$MODEL_NAME'."
else
    print_error "Failed to create Ollama model: '$MODEL_NAME'"
    print_error "Please review the output above for any errors (e.g., invalid GGUF, Ollama server not running)."
fi

# 5. Clean up the temporary Modelfile (the GGUF file is NOT deleted)
print_info "Cleaning up temporary Modelfile: '$MODELFILE_NAME'"
rm "$MODELFILE_NAME"

print_info "Script finished. Your GGUF file '$GGUF_FILE' remains untouched."