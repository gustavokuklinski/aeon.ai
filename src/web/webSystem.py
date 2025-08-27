import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, redirect
import json

# Add the parent directory to the Python path to import from 'core' and 'utils'
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import core modules from your project
from src.config import (
    OUTPUT_DIR, MEMORY_DIR
)
from src.core.ragSystem import ragSystem
from src.core.imgSystem import imgSystem
from src.utils.new import newConversation
from src.utils.conversation import loadConversation, saveConversation
from src.libs.messages import print_info_message, print_error_message, print_success_message

# Flask App Setup
app = Flask(__name__,
            template_folder=str(project_root / 'web' / 'templates'),
            static_folder=str(project_root / 'web' / 'assets'))

abs_output_dir = project_root / OUTPUT_DIR
abs_memory_dir = project_root / MEMORY_DIR

# Global RAG System state variables
rag_chain = None
vectorstore = None
text_splitter = None
llama_embeddings = None
llm_instance = None
current_memory_path = None
conversation_filename = None
current_conversation_id = None

def initialize_rag_system(conv_id):
    """
    Initializes or re-initializes the RAG system for a specific conversation ID.
    """
    global rag_chain, vectorstore, text_splitter, llama_embeddings, llm_instance, current_memory_path, conversation_filename, current_conversation_id

    # Reset existing components
    rag_chain = None
    vectorstore = None
    text_splitter = None
    llama_embeddings = None
    llm_instance = None
    current_memory_path = None
    conversation_filename = None

    print_info_message(f"Attempting to load conversation ID: {conv_id}")
    conv_dir_path = abs_memory_dir / conv_id
    if not conv_dir_path.is_dir():
        print_error_message(f"Conversation directory for ID '{conv_id}' not found.")
        return False
    
    try:
        rag_chain_temp, vectorstore_temp, text_splitter_temp, llama_embeddings_temp, llm_instance_temp = ragSystem(
            conversation_memory_path=conv_dir_path,
            chroma_db_dir_path=conv_dir_path / "db",
            is_new_session=False
        )
        rag_chain = rag_chain_temp
        vectorstore = vectorstore_temp
        text_splitter = text_splitter_temp
        llama_embeddings = llama_embeddings_temp
        llm_instance = llm_instance_temp
        current_memory_path = conv_dir_path
        conversation_filename = f"conversation_{conv_id}.json"
        current_conversation_id = conv_id
        print_success_message(f"Successfully loaded RAG system for conversation ID: {current_conversation_id}")
        return True
    except Exception as e:
        print_error_message(f"Error loading conversation '{conv_id}': {e}")
        return False


# Routes
@app.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html", initial_conv_id=None, initial_history=[])


@app.route("/chat/<string:conv_id>")
def load_conversation_page(conv_id):
    """Render the chat interface for a specific conversation ID and load its history."""
    conv_history = []
    history_file_path = abs_memory_dir / conv_id / f"conversation_{conv_id}.json"
    if history_file_path.exists():
        with open(history_file_path, "r") as f:
            conv_history = json.load(f)
            
    return render_template("index.html", initial_conv_id=conv_id, initial_history=conv_history)


@app.route("/new_chat", methods=["POST"])
def new_chat_route():
    try:
        session_vars = newConversation(abs_memory_dir)
        if session_vars and "conv_id" in session_vars:
            conv_id = session_vars["conv_id"]
            new_chat_url = url_for("load_conversation_page", conv_id=conv_id)
            print_success_message(f"Backend successfully generated new conversation ID: {conv_id}")
            return jsonify({"conversation_id": conv_id, "redirect_url": new_chat_url}), 200
        else:
            print_error_message("Backend failed to generate new conversation ID. Returned session_vars were missing 'conv_id' key.")
            return jsonify({"message": "Failed to retrieve conversation ID."}), 500
    except Exception as e:
        print_error_message(f"An exception occurred while creating new conversation: {e}")
        return jsonify({"message": f"Failed to create new conversation: {e}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    conv_id = data.get("conversation_id")

    if not user_input:
        return jsonify({"response": "No message provided."}), 400

    # If no conversation ID, create a new one first
    if not conv_id:
        try:
            session_vars = newConversation(abs_memory_dir)
            if not session_vars or "conv_id" not in session_vars:
                return jsonify({"response": "Failed to create a new conversation for your message."}), 500
            conv_id = session_vars["conv_id"]
        except Exception as e:
            return jsonify({"response": f"Failed to create new conversation for your message: {e}"}), 500
    
    # Initialize RAG system for the current or new conversation
    if not initialize_rag_system(conv_id):
        return jsonify({"response": f"Failed to initialize RAG system for conversation: {conv_id}"}), 500
           
    try:
        response = rag_chain.invoke(user_input)
        ai_response_content = str(response)

        saveConversation(user_input, ai_response_content, current_memory_path, conversation_filename)

        return jsonify({"response": ai_response_content, "conversation_id": current_conversation_id})
    except Exception as e:
        print(f"Error during RAG processing: {e}", file=sys.stderr)
        return jsonify({"response": "An error occurred. Please try again."}), 500


@app.route('/conversations', methods=["GET"])
def list_conversations_route():
    conversation_dirs = [d.name for d in abs_memory_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    conversations = [{"id": conv_id, "name": conv_id} for conv_id in sorted(conversation_dirs, reverse=True)]
    return jsonify(conversations)


@app.route('/conversation/<string:conv_id>', methods=["GET"])
def get_conversation_history(conv_id):
    conv_dir = abs_memory_dir / conv_id
    if not conv_dir.is_dir():
        return jsonify({"message": "Conversation not found."}), 404
    
    history_file_path = conv_dir / f"conversation_{conv_id}.json"
    if not history_file_path.exists():
        return jsonify({"message": "Conversation history file not found."}), 404
        
    try:
        history = loadConversation(conv_dir, f"conversation_{conv_id}.json")
        if not initialize_rag_system(conv_id):
            return jsonify({"message": f"Failed to load RAG system for conversation: {conv_id}"}), 500
        
        return jsonify(history)
    except Exception as e:
        return jsonify({"message": f"An error occurred while loading history: {e}"}), 500


@app.route('/serve_from_memory/<folder>/<path:filename>')
def serve_from_memory(folder, filename):
    if current_memory_path:
        base_dir = current_memory_path / folder
        if base_dir.is_dir():
            return send_from_directory(str(base_dir), filename)
    return "File not found", 404


if __name__ == "__main__":
    os.makedirs(abs_output_dir, exist_ok=True)
    app.run(debug=True, port=4303)
