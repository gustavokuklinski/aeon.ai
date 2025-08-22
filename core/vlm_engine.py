# core/vlm_engine.py
import os
from llama_cpp import Llama # LlamaCpp is now Llama in newer versions
from pathlib import Path
from core.config import (VLM_MODEL,LLM_N_CTX, LLM_MODEL)

def process_image_with_vlm(vlm_model_path: str, mmproj_model_path: str, image_path: str, prompt: str) -> str:
    """
    Initializes a VLM and processes an image-text prompt.

    Args:
        vlm_model_path (str): The path to the VLM GGUF model (e.g., SmolVLM).
        mmproj_model_path (str): The path to the multimodal projection model (e.g., mmproj).
        image_path (str): The path to the input image file.
        prompt (str): The user's text prompt for the image.

    Returns:
        str: The VLM's generated response.
    """
    try:
        if not all(map(os.path.exists, [vlm_model_path, mmproj_model_path, image_path])):
            return "Error: One or more required model or image files not found."

        # The Llama class in llama-cpp-python can handle multimodal models
        # by passing the mmproj path as an argument.
        llm = Llama(
            model_path=VLM_MODEL,
            n_ctx=LLM_N_CTX,
            n_batch=512,
            verbose=False,
            # This is the key parameter for multimodal support.
            clip_model_path=LLM_MODEL,
            stop=[
            "\n",
            ".",
            "USER:",
            "ASSISTANT:",
            "\n\n",
            ]
        )
        
        # Multimodal prompts have a specific format.
        # This example uses a common format but may need to be adjusted
        # for your specific model's template (e.g., ChatML, Llama-2).
        vlm_prompt = f"""
You are AEON, a helpful AI assistant.
Your goal is to provide a comprehensive and helpful response based on the user's question, the provided context, and the web search results.

Based on the image, answer the following question or affirmative of what you saw:
User: [{image_path}] {prompt}

"""
     
        
        # The invoke method handles the prompt with the embedded image data
        response = llm(vlm_prompt, max_tokens=256)
        
        return response['choices'][0]['text'].strip()

    except Exception as e:
        return f"An error occurred during VLM processing: {e}"