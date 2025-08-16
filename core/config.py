# core/config.py
import json
from pathlib import Path

# Configuration
INPUT_DIR = "./data/cerebrum"
CHROMA_DB_DIR = "./data/synapse"
OUTPUT_DIR = "./data/output"
CONFIG_FILE = "./config.json"

# Load Configuration from JSON
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    LLM_MODEL = config["llm_config"]["model"]
    LLM_TEMPERATURE = config["llm_config"]["temperature"]

    VLM_MODEL = config["vlm_config"]["model"]
    VLM_MODEL_WIDTH = config["vlm_config"]["width"]
    VLM_MODEL_HEIGHT = config["vlm_config"]["height"]
    VLM_MODEL_HARDWARE = config["vlm_config"]["hardware"]
    VLM_MODEL_NEGATIVE_PROMPT = config["vlm_config"]["negative_prompt"]

    EMBEDDING_MODEL = config["embedding_model"]
    SYSTEM_PROMPT = config.get("system_prompt", "You are a helpful AI assistant.\nContext: {context}")

except FileNotFoundError:
    print(f"\033[91m[ERROR]\033[0m {CONFIG_FILE} not found. Please create it with LLM, embedding model, and Moondream settings.")
    print("\033[91m[ERROR]\033[0m Example config.json:")
    print(json.dumps({
        "llm_config": {
            "model": "<YOUR_MODEL_HERE>",
            "temperature": 0.7
        },
        "vlm_config": {
            "model": "<YOUR_IMAGE_MODEL_HERE>",
            "width": 512,
            "height": 512,
            "hardware":"<CUDA_FOR_GPU__CPU_FOR_PC>",
            "torch_dtype": 32,
            "negative_prompt":"low quality, deformed, blurry, watermark, text"
        },
        "embedding_model": "<YOUR_EMBED_MODEL_HERE>",
        "system_prompt": "You are a helpful AI assistant. Your name is Aeon.\nContext: {context}"
    }, indent=2))
    exit()
except KeyError as e:
    print(f"\033[91m[ERROR]\033[0m Missing key in {CONFIG_FILE}: {e}. Please ensure 'llm_config.model', 'llm_config.temperature', 'embedding_model', and optionally 'system_prompt' are defined.")
    exit()

# Ensure OUTPUT_DIR exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)