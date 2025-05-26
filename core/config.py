# config.py
import json
from pathlib import Path

# --- Configuration ---
MARKDOWN_DATA_DIR = "./data/cerebrum"
CHROMA_DB_DIR = "./data/synapse"
OUTPUT_DIR = "./data/output"
CONFIG_FILE = "./config.json"

# --- Load Configuration from JSON ---
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    LLM_MODEL = config["llm_config"]["model"]
    LLM_TEMPERATURE = config["llm_config"]["temperature"]
    EMBEDDING_MODEL = config["embedding_model"]
    SYSTEM_PROMPT = config["system_prompt"]

    

except FileNotFoundError:
    print(f"\033[91m[ERROR]\033[0m {CONFIG_FILE} not found. Please create it with LLM and embedding model")
    print("\033[91m[ERROR]\033[0m Example config.json:")
    print(json.dumps({
        "llm_config": {
            "model": "smollm2:135m",
            "temperature": 1.0
        },
        "embedding_model": "nomic-embed-text",
        "system_prompt": "You are a helpful AI assistant. Answer questions ONLY from the provided context.\n\nContext: {context}"
    }, indent=2))
    exit()
except KeyError as e:
    print(f"\033[91m[ERROR]\033[0m Missing key in {CONFIG_FILE}: {e}. Please ensure 'llm_config.model', 'llm_config.temperature', 'embedding_model', 'system_prompt' are defined.")
    exit()

# Ensure OUTPUT_DIR exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)