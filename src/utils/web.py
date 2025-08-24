# src/web.py
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Add the parent directory to the Python path to import from 'core'
#sys.path.append('..')
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import core modules from your project
from src.config import (
    LLM_MODEL, EMBEDDING_MODEL, OUTPUT_DIR, INPUT_DIR
)
from core.rag_setup import initialize_rag_system
from core.image_gen import generate_image_from_prompt
from core.ingestion import ingest_documents # Import the ingestion function

# Flask App Setup
# app = Flask(__name__, template_folder='../web/templates', static_folder='../web/assets')
app = Flask(__name__, template_folder=str(project_root / 'web' / 'templates'), static_folder=str(project_root / 'web' / 'assets'))
abs_output_dir = str(project_root / OUTPUT_DIR)
abs_input_dir = str(project_root / INPUT_DIR)

# RAG System Initialization (runs once on app startup)
rag_chain = None
vectorstore = None
text_splitter = None
ollama_embeddings = None

def initialize_rag_system_for_web():
    """Wrapper function to initialize the RAG system for the web app."""
    global rag_chain, vectorstore, text_splitter, ollama_embeddings
    
    # Call the new shared function
    rag_chain, vectorstore, text_splitter, ollama_embeddings = initialize_rag_system()

# Routes
@app.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests, process with RAG, and return a response."""
    data = request.get_json()
    user_input = data.get("message", "").strip()
    
    if not user_input:
        return jsonify({"response": "No message provided."}), 400

    # Handle the /image command
    if user_input.startswith('/image'):
        image_prompt = user_input.replace('/image', '', 1).strip()
        if not image_prompt:
            return jsonify({"response": "Please provide a prompt for image generation, e.g., /image a cat on a beach."}), 400

        try:
            image_path = generate_image_from_prompt(image_prompt, OUTPUT_DIR)
            if image_path:
                # Get the filename from the path
                image_filename = os.path.basename(image_path)
                # Create a URL to the image using Flask's static folder
                image_url = url_for('static_images', filename=image_filename)
                # Return the URL in a specific format for the frontend to handle
                return jsonify({"response": f"Image generated: {image_prompt}", "image_url": image_url})
            else:
                return jsonify({"response": "Failed to generate image."}), 500
        except Exception as e:
            print(f"Error during image generation: {e}", file=sys.stderr)
            return jsonify({"response": "An error occurred during image generation. Please try again."}), 500

    # If not an image command, process with RAG
    try:
        response = rag_chain.invoke(user_input)
        # ... (rest of the chat logic remains the same)
        if isinstance(response, list) and response:
            ai_response_content = response[0].get("generated_text", "")
        else:
            ai_response_content = str(response)

        # Remove chat template tags
        clean_response = ai_response_content.replace("<|im_start|>system", "").replace("<|im_end|>", "").replace("<|im_start|>user", "").replace("<|im_start|>assistant", "").strip()
        clean_response = clean_response.lstrip('\n ').strip()
        clean_response = '\n'.join([line for line in clean_response.split('\n') if line.strip()])

        return jsonify({"response": clean_response})
    except Exception as e:
        print(f"Error during RAG processing: {e}", file=sys.stderr)
        return jsonify({"response": "An error occurred. Please try again."}), 500

# New route for file upload and ingestion
@app.route("/upload_and_ingest", methods=["POST"])
def upload_and_ingest_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file."}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(abs_input_dir, filename)
        
        try:
            # Save the file to the input directory
            file.save(filepath)
            
            # Ingest the saved file using the existing function
            ingest_documents(filepath, vectorstore, text_splitter, llama_embeddings)
            
            return jsonify({"message": f"File '{filename}' ingested successfully!"}), 200
        except Exception as e:
            print(f"Error during file ingestion: {e}", file=sys.stderr)
            return jsonify({"message": f"An error occurred during ingestion: {e}"}), 500

# Add a route to serve the generated images
@app.route('/images/<path:filename>')
def static_images(filename):
    """Serve generated images from the output directory."""
    return send_from_directory(abs_output_dir, filename)


# Run the app
if __name__ == "__main__":
    initialize_rag_system_for_web()
    # Ensure the output directory exists
    os.makedirs(abs_output_dir, exist_ok=True)
    app.run(debug=True, port=4303)