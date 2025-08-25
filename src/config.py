# src/config.py
import yaml
from pathlib import Path

from src.libs.messages import *

# Configuration
MEMORY_DIR = "./data/memory"
INPUT_DIR = "./data/cerebrum/system"
CHROMA_DB_DIR = "./data/cerebrum/memory"
BACKUP_DIR = "./data/output/backup"
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
    VLM_MODEL_HARDWARE = config["vlm_config"]["hardware"]
    VLM_TEMPERATURE = config["vlm_config"]["temperature"]

    IMG_MODEL = config["img_config"]["model"]
    IMG_MODEL_WIDTH = config["img_config"]["width"]
    IMG_MODEL_HEIGHT = config["img_config"]["height"]
    IMG_MODEL_HARDWARE = config["img_config"]["hardware"]
    IMG_MODEL_NEGATIVE_PROMPT = config["img_config"]["negative_prompt"]

    EMB_MODEL = config["emb_config"]["model"]
    EMB_N_CTX = config["emb_config"]["n_ctx"]
    EMB_CHUNK_SIZE = config["emb_config"]["chunk_size"]
    EMB_CHUNK_OVERLAP = config["emb_config"]["chunk_overlap"]

except FileNotFoundError:
    print_error_message(f"Config file not found: {CONFIG_FILE}")

    exit()
except KeyError as e:
    print(f"\033[91m[ERROR]\033[0m Missing key in {CONFIG_FILE}: {e}.")
    exit()

# Ensure OUTPUT_DIR exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)