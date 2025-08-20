# core/image_gen.py
import os
import hashlib
from pathlib import Path
from transformers import CLIPTextModel
from diffusers import StableDiffusionPipeline
import torch
from core.config import (VLM_MODEL, VLM_MODEL_WIDTH, 
VLM_MODEL_HEIGHT, VLM_MODEL_HARDWARE, 
VLM_MODEL_NEGATIVE_PROMPT)

def generate_image_from_prompt(prompt: str, output_dir: str):
    """
    Generates an image from a text prompt using a pre-trained Stable Diffusion model
    and saves it to the specified output directory with a unique filename.
    """
    print("\033[1;34m[INFO]\033[0m Initializing image generation pipeline...")
    try:
      
        pipe = StableDiffusionPipeline.from_pretrained(
            VLM_MODEL,
            local_files_only=True
        )
        pipe = pipe.to(VLM_MODEL_HARDWARE)
        print("\033[1;32m[SUCCESS]\033[0m Image generation model loaded.")
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m Failed to load image generation model: {e}")
        return

    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\033[1;34m[INFO]\033[0m Generating image...")
    try:
        negative_prompt = VLM_MODEL_NEGATIVE_PROMPT
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=VLM_MODEL_WIDTH,
            height=VLM_MODEL_HEIGHT,
        ).images[0]

        # Generate a unique filename using an MD5 hash of the prompt and a timestamp
        unique_name = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        filename = f"image_{unique_name}.png"
        filepath = output_path / filename

        image.save(filepath)
        print(f"\033[1;32m[SUCCESS]\033[0m Image saved to {filepath}")
        return str(filepath)

    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m An error occurred during image generation: {e}")
        return None