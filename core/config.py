# core/config.py
import yaml
from pathlib import Path

# Configuration
INPUT_DIR = "./data/cerebrum"
CHROMA_DB_DIR = "./data/synapse"
OUTPUT_DIR = "./data/output"
CONFIG_FILE = "./config.yml"

# Load Configuration from YAML
try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    LLM_MODEL = config["llm_config"]["model"]
    LLM_TEMPERATURE = config["llm_config"]["temperature"]

    VLM_MODEL = config["img_config"]["model"]
    VLM_MODEL_WIDTH = config["img_config"]["width"]
    VLM_MODEL_HEIGHT = config["img_config"]["height"]
    VLM_MODEL_HARDWARE = config["img_config"]["hardware"]
    VLM_MODEL_NEGATIVE_PROMPT = config["img_config"]["negative_prompt"]

    EMBEDDING_MODEL = config["embedding_model"]
    SYSTEM_PROMPT = config.get("system_prompt", "You are a helpful AI assistant.\nContext: {context}")

except FileNotFoundError:
    print(f"\033[91m[ERROR]\033[0m {CONFIG_FILE} not found. Please create it with LLM, embedding model, and image settings.")
    print("\033[91m[ERROR]\033[0m Example config.yml:")
    print("""llm_config:
  model: HuggingFaceTB/SmolLM2-135M
  temperature: 0.5
img_config:
  model: segmind/tiny-sd
  width: 512
  height: 512
  hardware: cpu
  negative_prompt: low quality, deformed, blurry, watermark, text
embedding_model: sentence-transformers/all-MiniLM-L6-v2
system_prompt: "You are a helpful AI assistant. Your name is Aeon.\nContext: {context}"
""")
    exit()
except KeyError as e:
    print(f"\033[91m[ERROR]\033[0m Missing key in {CONFIG_FILE}: {e}.")
    exit()

# Ensure OUTPUT_DIR exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)