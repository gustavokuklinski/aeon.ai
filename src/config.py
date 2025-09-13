# src/config.py
import yaml
from pathlib import Path
import shutil

from src.libs.messages import (
    print_error_message,
    print_info_message,
    print_success_message,
)

# Configuration dirs
MEMORY_DIR = "./data/chats"
INPUT_DIR = "./data/input"
CHROMA_DB_DIR = "./data/chats"
BACKUP_DIR = "./data/output/backup"
OUTPUT_DIR = "./data/output"


CONFIG_FILE = "./config.yml"



PLUGINS_DIR = Path("./plugins")

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
    SYSTEM_RAG_PROMPT = config["llm_config"]["llm_rag_prompt"]

    EMB_MODEL = config["emb_config"]["model"]
    EMB_N_CTX = config["emb_config"]["n_ctx"]
    EMB_CHUNK_SIZE = config["emb_config"]["chunk_size"]
    EMB_CHUNK_OVERLAP = config["emb_config"]["chunk_overlap"]
    LOADED_PLUGINS = config["load_plugins"]
except FileNotFoundError:
    print_error_message(f"Config file not found: {CONFIG_FILE}")

    exit()
except KeyError as e:
    print_error_message(f"Missing key in {CONFIG_FILE}: {e}.")
    exit()

PLUGINS_CONFIGS = {}
if PLUGINS_DIR.is_dir():
    for plugin_path in PLUGINS_DIR.iterdir():
        if plugin_path.is_dir():
            plugin_config_file = plugin_path / "config.yml"
            if plugin_config_file.exists():
                try:
                    with open(plugin_config_file, 'r', encoding='utf-8') as f:
                        plugin_config = yaml.safe_load(f)
                        # Store the entire aeon_plugin section
                        if "aeon_plugin" in plugin_config:
                            # Use plugin's command or a unique identifier as key
                            cmd = plugin_config["aeon_plugin"].get(
                                "command", plugin_path.name)
                            PLUGINS_CONFIGS[cmd] = {
                                "config_data": plugin_config["aeon_plugin"],
                                "plugin_dir": plugin_path  # Store the plugin's root directory
                            }
                        else:
                            print_error_message(
                                f"Missing 'aeon_plugin' key in {plugin_config_file}.")
                except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
                    print_error_message(
                        f"Error loading plugin config '{plugin_config_file}': {e}")
            else:
                print_info_message(
                    f"Skipping plugin '{plugin_path.name}': config.yml not found.")
else:
    print_info_message(f"Plugins directory not found at {PLUGINS_DIR}.")

# Ensure OUTPUT_DIR exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def copy_config_to_chat(conversation_id: str):
    """
    Copies the main config.yml to a new conversation directory.
    """
    source_path = Path(CONFIG_FILE)
    destination_dir = Path(MEMORY_DIR) / conversation_id
    destination_path = destination_dir / "config.yml"

    if not source_path.exists():
        print_error_message(f"Source config file not found at {source_path}.")
        return False

    try:
        shutil.copyfile(source_path, destination_path)
        print_success_message(f"Copied config.yml to {destination_path}")
        return True
    except FileNotFoundError:
        print_error_message(f"Destination directory not found: {destination_dir}")
        return False
    except Exception as e:
        print_error_message(f"Error copying config file: {e}")
        return False