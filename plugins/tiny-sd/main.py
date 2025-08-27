import hashlib
from pathlib import Path
from diffusers import StableDiffusionPipeline
import torch

from src.libs.messages import (print_info_message, print_success_message,
                               print_error_message)


_pipeline = None

if torch.cuda.is_available():
    DEVICE = "cuda"
    print_info_message("Using GPU for image generation.")
else:
    DEVICE = "cpu"
    print_info_message("No GPU found, using CPU for image generation. This may be slow.")


def get_pipeline(plugin_config: dict, plugin_dir: Path):

    global _pipeline
    if _pipeline is None:
        if not plugin_config:
            print_error_message("Cannot initialize pipeline, plugin configuration not provided.")
            return None

        model_path_str = plugin_config.get("model_path")
        if not model_path_str:
            print_error_message("Model path is missing in plugin configuration.")
            return None
        
        model_path = plugin_dir / model_path_str
        if not model_path.exists():
            print_error_message(f"Model path not found: {model_path}")
            return None

        print_info_message(f"Initializing image generation pipeline from {model_path}...")
        try:
            _pipeline = StableDiffusionPipeline.from_pretrained(
                model_path,
                local_files_only=True,
            )
            _pipeline = _pipeline.to(DEVICE)
            print_success_message("Image generation model loaded successfully.")
        except Exception as e:
            print_error_message(f"Failed to load image generation model: {e}")
            _pipeline = None
            
    return _pipeline


def run_plugin(prompt: str, **kwargs) -> None:
    plugin_config = kwargs.get('plugin_config')
    plugin_dir = kwargs.get('plugin_dir')
    output_dir = kwargs.get('output_dir')

    if not plugin_config or not plugin_dir:
        print_error_message("Plugin configuration or directory not provided.")
        return

    if not prompt:
        print_error_message("A prompt is required for image generation.")
        return

    if not output_dir:
        print_error_message("Output directory not provided for image saving.")
        return

    pipe = get_pipeline(plugin_config, plugin_dir)
    if not pipe:
        print_error_message("Image generation pipeline is not available.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    print_info_message("Generating image...")
    try:
        image = pipe(
            prompt=prompt,
            width=512,
            height=512,
        ).images[0]

        unique_name = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        filename = f"image_{unique_name}.png"
        filepath = output_dir / filename

        image.save(filepath)
        print_success_message(f"Image saved to {filepath}")

    except Exception as e:
        print_error_message(f"An error occurred during image generation: {e}")
        return