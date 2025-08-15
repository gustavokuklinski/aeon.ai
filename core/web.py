# core/web.py
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Add the parent directory to the Python path to import from 'core'
sys.path.append('..')

# Import core modules from your project
from core.config import (
    LLM_MODEL, EMBEDDING_MODEL
)
from core.ingestion import ingest_documents
from core.rag_setup import initialize_rag_system # New import

# Flask App Setup
app = Flask(__name__, template_folder='../web/templates', static_folder='../web/assets')

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

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat requests and return AI responses."""
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Handle '/ingest' command
        if user_input.lower().startswith("/ingest "):
            ingest_path = user_input[len("/ingest "):].strip()
            ingest_documents(ingest_path, vectorstore, text_splitter, ollama_embeddings)
            response_text = f"Successfully ingested documents from '{ingest_path}'. Knowledge base updated."
        else:
            response = rag_chain.invoke(user_input)
            response_text = response

        return jsonify({"response": response_text})
    except Exception as e:
        print(f"Error during RAG processing: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

# Run the app
if __name__ == "__main__":
    initialize_rag_system_for_web()
    app.run(debug=True, port=4303)