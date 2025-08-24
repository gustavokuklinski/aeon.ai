# src/external/vlmSystem.py
import os
from llama_cpp import Llama
from pathlib import Path

from src.config import (
    VLM_PROMPT,
    VLM_MODEL, 
    VLM_N_CTX, 
    VLM_TEMPERATURE, 
    VLM_MODEL_MMPROJ, 
    VLM_TEMPERATURE,
    VLM_TOP_K,
    VLM_TOP_P
)

from src.utils.messages import *

def vlmSystem(image_path: str, prompt: str) -> str:

# Test query: /view /home/gustavokuklinski/Projects/aeon.ai/data/output/planet.png Describe this image. What is the color of the sky?

    try:
        if not Path(image_path).exists():
            error_msg = f"Image file not found at: {image_path}"
            print_error_message(error_msg)
            return f"I couldn't find the image you specified. {error_msg}"

        vllm = Llama(
            model_path=VLM_MODEL,
            n_ctx=VLM_N_CTX,
            n_batch=1024,
            verbose=False,
            clip_model_path=VLM_MODEL_MMPROJ,
            stop=["<|im_end|>", "\nQUESTION:", "\nCONTEXT:", "RESPONSE:"],
            temperature=VLM_TEMPERATURE,
            top_p=VLM_TOP_P,
            top_k=VLM_TOP_K
        )

        # Corrected prompt template and VLM call
        vlm_prompt = (
            f"<|im_start|>system\n"
            f"{VLM_PROMPT}\n"
            f"<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Image:\n"
            f"QUESTION:{prompt}\n"
            f"<|im_end|>\n"
            f"<|im_start|>assistant\n"
            f"RESPONSE:"
        )

        response = vllm.create_chat_completion(
            messages=[
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_path}},
                    {"type": "text", "text": prompt}
                ]}
            ],
            stream=False,
        )

        print(f"\033[1;34m[VLM]\033[0m", response['choices'][0]['message']['content'].strip())
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        error_msg = f"An unexpected error occurred during VLM processing: {type(e).__name__}: {e}"
        print_error_message(error_msg)
        return f"I'm sorry, an unexpected error occurred while processing the image: {error_msg}. Please try again."
