# src/external/imageGenerator.py
import os
import hashlib
from pathlib import Path

from transformers import CLIPTextModel
from diffusers import StableDiffusionPipeline
import torch

from src.config import (
    IMG_MODEL,
    IMG_MODEL_WIDTH, 
    IMG_MODEL_HEIGHT, 
    IMG_MODEL_HARDWARE, 
    IMG_MODEL_NEGATIVE_PROMPT
)

from src.utils.messages import *

def imageGenerator(prompt: str, output_dir: str):
    print_info_message(f"Initializing image generation pipeline...")
    try:
      
        pipe = StableDiffusionPipeline.from_pretrained(
            IMG_MODEL,
            local_files_only=True
        )
        pipe = pipe.to(IMG_MODEL_HARDWARE)
        print_success_message("Image generation model loaded.")
    except Exception as e:
        print_error_message(f"Failed to load image generation model: {e}")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print_info_message("Generating image...")
    try:
        negative_prompt = IMG_MODEL_NEGATIVE_PROMPT
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=IMG_MODEL_WIDTH,
            height=IMG_MODEL_HEIGHT,
        ).images[0]

        unique_name = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        filename = f"image_{unique_name}.png"
        filepath = output_path / filename

        image.save(filepath)
        print_success_message(f"Image saved to {filepath}")
        return str(filepath)

    except Exception as e:
        print_error_message(f"An error occurred during image generation: {e}")
        return None