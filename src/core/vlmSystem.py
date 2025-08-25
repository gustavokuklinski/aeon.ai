# src/external/vlmSystem.py
import os
from pathlib import Path

from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
import torch


from src.config import (
    VLM_MODEL,
    VLM_TEMPERATURE,
    VLM_MODEL_HARDWARE,
    VLM_TEMPERATURE,
)

from src.libs.messages import *

def vlmSystem(image_path: str, prompt: str) -> str:

    try:
        if not Path(image_path).exists():
            error_msg = f"Image file not found at: {image_path}"
            print_error_message(error_msg)
            return f"I couldn't find the image you specified. {error_msg}"

        print_info_message(f"Initializing VLM pipeline for {VLM_MODEL}...")

        # Define the device
        device = VLM_MODEL_HARDWARE

        processor = AutoProcessor.from_pretrained(VLM_MODEL, local_files_only=True)
        model = AutoModelForVision2Seq.from_pretrained(VLM_MODEL, local_files_only=True)
        model.to(device)

        print_success_message("VLM model loaded.")

        image = Image.open(image_path).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": f"{prompt}"}
                ]
            },
        ]
        prompt = processor.apply_chat_template(messages, add_generation_prompt=False)
        inputs = processor(text=prompt, images=image, return_tensors="pt").to(device)

        generated_ids = model.generate(**inputs, max_new_tokens=256)
        generated_text = processor.batch_decode(
            generated_ids, 
            skip_special_tokens=True
        )

        # print(f"\033[1;34m[VLM]\033[0m", generated_text[0])
        
        return generated_text[0]

    except Exception as e:
        error_msg = f"An unexpected error occurred during VLM processing: {type(e).__name__}: {e}"
        print_error_message(error_msg)
        return f"I'm sorry, an unexpected error occurred while processing the image: {error_msg}. Please try again."
