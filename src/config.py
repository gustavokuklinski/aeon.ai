# src/config.py
import yaml
from pathlib import Path

from src.utils.messages import *

# Configuration
INPUT_DIR = "./data/cerebrum/system"
MEMORY_DIR = "./data/cerebrum/memory"
CHROMA_DB_DIR = "./data/cerebrum/memory"
OUTPUT_DIR = "./data/output"
CONFIG_FILE = "./config.yml"

# Load Configuration from YAML
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    LLM_MODEL = config["llm_config"]["model"]
    LLM_TEMPERATURE = config["llm_config"]["temperature"]
    LLM_N_CTX = config["llm_config"]["n_ctx"]
    LLM_TOP_K = config["llm_config"]["top_k"]
    LLM_TOP_P = config["llm_config"]["top_p"]
    SYSTEM_PROMPT = config["llm_config"]["llm_prompt"]

    VLM_MODEL = config["vlm_config"]["model"]
    VLM_MODEL_MMPROJ = config["vlm_config"]["mmproj"]
    VLM_TEMPERATURE = config["vlm_config"]["temperature"]
    VLM_N_CTX = config["vlm_config"]["n_ctx"]
    VLM_TOP_K = config["vlm_config"]["top_k"]
    VLM_TOP_P = config["vlm_config"]["top_p"]
    VLM_PROMPT = config["vlm_config"]["vlm_prompt"]

    IMG_MODEL = config["img_config"]["model"]
    IMG_MODEL_WIDTH = config["img_config"]["width"]
    IMG_MODEL_HEIGHT = config["img_config"]["height"]
    IMG_MODEL_HARDWARE = config["img_config"]["hardware"]
    IMG_MODEL_NEGATIVE_PROMPT = config["img_config"]["negative_prompt"]

    EMBEDDING_MODEL = config["embedding_model"]

except FileNotFoundError:
    print_error_message(f"Config file not found: {CONFIG_FILE}")

    exit()
except KeyError as e:
    print(f"\033[91m[ERROR]\033[0m Missing key in {CONFIG_FILE}: {e}.")
    exit()

# Ensure OUTPUT_DIR exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)