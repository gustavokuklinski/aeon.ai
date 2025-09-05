from pathlib import Path

from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
import torch

from src.libs.messages import (print_info_message, print_success_message,
                               print_error_message)


_processor = None
_model = None

if torch.cuda.is_available():
    DEVICE = "cuda"
    print_info_message("Using GPU for VLM processing.")
else:
    DEVICE = "cpu"
    print_info_message("No GPU found, using CPU for VLM processing. This may be slow.")


def get_pipeline(plugin_config: dict, plugin_dir: Path):
    global _processor, _model

    if _processor is None or _model is None:
        if not plugin_config:
            print_error_message("VLM pipeline cannot be initialized; plugin configuration not provided.")
            return None, None

        model_path_str = plugin_config.get("model_path")
        
        if not model_path_str:
            print_error_message("Model ID or path is missing in plugin configuration.")
            return None, None
            
        full_model_path = plugin_dir / model_path_str

        print_info_message(f"Initializing VLM pipeline for {model_path_str}...")
        try:
            _processor = AutoProcessor.from_pretrained(
                full_model_path, local_files_only=True, cache_dir=full_model_path.parent
            )
            _model = AutoModelForVision2Seq.from_pretrained(
                full_model_path, local_files_only=True, cache_dir=full_model_path.parent
            )
            _model.to(DEVICE)
            print_success_message("VLM model and processor loaded successfully.")
        except Exception as e:
            print_error_message(f"Failed to load VLM model: {e}")
            _processor, _model = None, None  # Reset on failure

    return _processor, _model


def run_plugin(image_path: str, prompt: str, **kwargs) -> str:
    plugin_config = kwargs.get('plugin_config')
    plugin_dir = kwargs.get('plugin_dir')
    
    if not plugin_config or not plugin_dir:
        print_error_message("Plugin configuration or directory not provided.")
        return

    if not image_path:
        print_error_message("An image path is required for VLM processing.")
        return

    processor, model = get_pipeline(plugin_config, plugin_dir)
    if not processor or not model:
        print_error_message("VLM pipeline is not available. Check plugin configuration and model files.")
        return

    image_file = Path(image_path)
    if not image_file.exists():
        print_error_message(f"Image file not found at: {image_file}")
        return

    print_info_message(f"Processing image '{image_file.name}' with prompt: '{prompt}'...")
    try:
        image = Image.open(image_file).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": f"{prompt}"}
                ]
            },
        ]
        
        input_prompt = processor.apply_chat_template(messages, add_generation_prompt=False, tokenize=False)
        inputs = processor(
            text=input_prompt,
            images=image,
            return_tensors="pt"
        ).to(DEVICE)

        generated_ids = model.generate(**inputs, max_new_tokens=256)
        generated_text = processor.batch_decode(
            generated_ids,
            skip_special_tokens=True
        )

        final_response = f"VLM Response: {generated_text[0]}"
        print_success_message(final_response)
        return

    except Exception as e:
        error_msg = f"An error occurred during VLM processing: {type(e).__name__}: {e}"
        print_error_message(error_msg)
        return