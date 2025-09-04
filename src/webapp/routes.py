# /src/webapp/routes.py
import os
import sys
import json
import shutil
import zipfile
import yaml
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import request, jsonify, render_template, url_for, send_from_directory

from src.config import LLM_MODEL, EMB_MODEL
from src.utils.new import newConversation
from src.utils.conversation import loadConversation, saveConversation
from src.utils.rename import renameConversationForWeb
from src.utils.load import loadBackup
from src.webapp.ragweb import initialize_rag_system, rag_system_state
from src.utils.ingestion import ingestDocuments
from src.utils.webSearch import webSearch

def init_routes(app, abs_output_dir, abs_memory_dir):

    os.makedirs(abs_output_dir, exist_ok=True)
    os.makedirs(abs_memory_dir, exist_ok=True)
    
    backup_dir = abs_output_dir / "backup"
    os.makedirs(backup_dir, exist_ok=True)

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            initial_conv_id=None,
            initial_history=[],
            llm_model=str(LLM_MODEL),
            llm_embeding=str(EMB_MODEL),
        )

    @app.route("/chat/<string:conv_id>")
    def load_conversation_page(conv_id):
        conv_history = []
        history_file_path = abs_memory_dir / conv_id / f"{conv_id}.json"
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
                return jsonify({"conversation_id": conv_id, "redirect_url": new_chat_url}), 200
            else:
                return jsonify({"message": "Failed to retrieve conversation ID."}), 500
        except Exception as e:
            return jsonify({"message": f"Failed to create new conversation: {e}"}), 500

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        user_input = data.get("message", "").strip()
        conv_id = data.get("conversation_id")

        if not user_input:
            return jsonify({"response": "No message provided."}), 400

        if not conv_id:
            try:
                session_vars = newConversation(abs_memory_dir)
                if not session_vars or "conv_id" not in session_vars:
                    return jsonify({"response": "Failed to create a new conversation for your message."}), 500
                conv_id = session_vars["conv_id"]
            except Exception as e:
                return jsonify({"response": f"Failed to create new conversation for your message: {e}"}), 500
        
        if conv_id not in rag_system_state:
            initialized_vars = initialize_rag_system(conv_id, abs_memory_dir)
            if not initialized_vars:
                return jsonify({"response": f"Failed to initialize RAG system for conversation: {conv_id}"}), 500
            rag_system_state[conv_id] = initialized_vars
        
        try:
            current_rag = rag_system_state[conv_id]
            response = current_rag["rag_chain"].invoke(user_input)
            ai_response_content = str(response)

            saveConversation(
                user_input, 
                ai_response_content, 
                current_rag["current_memory_path"], 
                current_rag["conversation_filename"]
            )

            return jsonify({"response": ai_response_content, "conversation_id": conv_id})
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
        
        history_file_path = conv_dir / f"{conv_id}.json"
        if not history_file_path.exists():
            return jsonify({"message": "Conversation history file not found."}), 404
            
        try:
            history = loadConversation(conv_dir, f"{conv_id}.json")
            return jsonify(history)
        except Exception as e:
            return jsonify({"message": f"An error occurred while loading history: {e}"}), 500

    @app.route('/delete_conversation/<string:conv_id>', methods=["DELETE"])
    def delete_conversation_route(conv_id):
        conv_dir_path = abs_memory_dir / conv_id
        if not conv_dir_path.is_dir():
            return jsonify({"message": "Conversation not found."}), 404
        
        try:
            shutil.rmtree(conv_dir_path)
            return jsonify({"message": "Conversation deleted successfully."}), 200
        except Exception as e:
            return jsonify({"message": f"Failed to delete conversation: {e}"}), 500


    @app.route('/rename_conversation/<string:conv_id>', methods=["PATCH"])
    def rename_conversation_route(conv_id):
        data = request.get_json()
        new_name = data.get('name')
        
        if not conv_id or not new_name:
            return jsonify({"message": "Missing conversation ID or new name."}), 400

        success, message = renameConversationForWeb(conv_id, new_name, abs_memory_dir)
        
        if success:
            return jsonify({"message": "Conversation renamed successfully.", "new_name": message}), 200
        else:
            return jsonify({"message": message}), 500


    @app.route('/load_backup', methods=['POST'])
    def load_backup_route():
        if 'file' not in request.files:
            return jsonify({"message": "No file part in the request."}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"message": "No selected file."}), 400
        
        if not file.filename.endswith('.zip'):
            return jsonify({"message": "Invalid file type. Please upload a .zip file."}), 400

        filename = secure_filename(file.filename)
        zip_path = abs_output_dir / filename
        
        try:
            file.save(zip_path)
            new_conv_id = loadBackup(zip_path, abs_memory_dir)
            
            if new_conv_id:
                return jsonify({"message": "Backup loaded successfully.", "redirect_url": url_for("load_conversation_page", conv_id=new_conv_id)}), 200
            else:
                return jsonify({"message": "Failed to load backup."}), 500
        except Exception as e:
            return jsonify({"message": f"An error occurred during the backup upload: {e}"}), 500
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)


    @app.route('/zip_backup/<string:conv_id>')
    def zip_backup_route(conv_id):
        conv_dir_path = abs_memory_dir / conv_id
        if not conv_dir_path.is_dir():
            return jsonify({"message": "Conversation not found."}), 404

        zip_filename = f"{conv_id}_web_backup.zip"
        zip_path = backup_dir / zip_filename

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(conv_dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, conv_dir_path.parent)
                        zipf.write(file_path, arcname)
            
            return jsonify({"message": "Backup created.", "zip_file": zip_filename}), 200

        except Exception as e:
            return jsonify({"message": f"Failed to create backup: {e}"}), 500


    @app.route('/download_backup/<path:filename>')
    def download_backup_route(filename):
        file_path = backup_dir / filename
        if not file_path.is_file():
            return "File not found.", 404

        try:
            response = send_from_directory(str(backup_dir), filename, as_attachment=True)
            @response.call_on_close
            def on_close():
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            return response
        except Exception:
            return "An error occurred during download.", 500


    @app.route('/serve_from_memory/<folder>/<path:filename>')
    def serve_from_memory(folder, filename):
        current_conv_id = request.args.get('conv_id')
        if current_conv_id:
            current_memory_path = abs_memory_dir / current_conv_id
            base_dir = current_memory_path / folder
            if base_dir.is_dir():
                return send_from_directory(str(base_dir), filename)
        return "File not found", 404

    @app.route('/api/config/<conv_id>', methods=['GET'])
    def get_config(conv_id):
        config_path = abs_memory_dir / conv_id / 'config.yml'
        if not config_path.is_file():
            return jsonify({"message": "Configuration file not found."}), 404
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({"config_content": content})
        except Exception as e:
            return jsonify({"message": f"Failed to read config file: {e}"}), 500

    @app.route('/api/config/<conv_id>', methods=['POST'])
    def save_config(conv_id):
        data = request.json
        config_content = data.get('config_content')
        if config_content is None:
            return jsonify({"message": "No configuration content provided."}), 400

        config_path = abs_memory_dir / conv_id / 'config.yml'
        
        try:
            yaml.safe_load(config_content)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
                
            return jsonify({"message": "Configuration saved successfully."})
        except yaml.YAMLError as e:
            return jsonify({"message": f"Invalid YAML content: {e}"}), 400
        except Exception as e:
            return jsonify({"message": f"Failed to save config file: {e}"}), 500
    
    @app.route('/ingest', methods=['POST'])
    def ingest_files():
        if 'file' not in request.files:
            return jsonify({"message": "No file part in the request."}), 400

        file = request.files['file']
        conv_id = request.form.get('conversation_id')
        print(conv_id)
        if file.filename == '':
            return jsonify({"message": "No selected file."}), 400

        allowed_extensions = {'.md', '.txt', '.json'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({"message": f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}"}), 400

        if not conv_id:
            return jsonify({"message": "Invalid conversation ID or RAG system not initialized."}), 400

        # Initialize RAG system if it's not already initialized for this conversation
        if conv_id not in rag_system_state:
            initialized_vars = initialize_rag_system(conv_id, abs_memory_dir)
            if not initialized_vars:
                return jsonify({"message": f"Failed to initialize RAG system for conversation: {conv_id}"}), 500
            rag_system_state[conv_id] = initialized_vars

        current_rag = rag_system_state[conv_id]
        temp_ingest_dir = current_rag["current_memory_path"] / 'temp_ingest'
        os.makedirs(temp_ingest_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        temp_file_path = temp_ingest_dir / filename
        
        try:
            file.save(temp_file_path)
            ingestDocuments(
                str(temp_file_path),
                current_rag["vectorstore"],
                current_rag["text_splitter"],
                current_rag["llama_embeddings"]
            )
            return jsonify({"message": f"File '{filename}' ingested successfully."}), 200
        except Exception as e:
            return jsonify({"message": f"An error occurred during file ingestion: {e}"}), 500
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @app.route('/search', methods=['POST'])
    def web_search_route():
        try:
            search_term = request.json.get('search_term')
            conv_id = request.json.get('conversation_id')
            
            if not conv_id:
                return jsonify({"message": "Conversation ID is required."}), 400
            
            if conv_id not in rag_system_state:
                initialized_vars = initialize_rag_system(conv_id, abs_memory_dir)
                if not initialized_vars:
                    return jsonify({"response": f"Failed to initialize RAG system for conversation: {conv_id}"}), 500
                rag_system_state[conv_id] = initialized_vars

            current_rag = rag_system_state[conv_id]
            
            summary = webSearch(
                search_term,
                current_rag["llm_instance"],
                current_rag["text_splitter"],
                current_rag["vectorstore"]
            )

            saveConversation(
                f"/search {search_term}",
                summary,
                current_rag["current_memory_path"],
                current_rag["conversation_filename"]
            )

            return jsonify({'response': summary})
        
        except Exception as e:
            print(f"Web search route failed: {e}", file=sys.stderr)
            return jsonify({"message": "An error occurred during the web search."}), 500