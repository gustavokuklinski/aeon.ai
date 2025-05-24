import base64
import requests
from PIL import Image
import io
from pathlib import Path

def get_image_description(image_path: str, ollama_url: str, vision_model_name: str) -> str:
    """
    Sends an image to the Ollama API with the specified vision model and returns a textual description.
    """
    if not Path(image_path).is_file():
        return f"\033[91m[ERROR]\033[0m Image file not found at '{image_path}'."

    try:
        with Image.open(image_path) as img:
            img.thumbnail((256, 256)) # Resize to a reasonable size to save bandwidth/memory
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=img.format if img.format else "PNG")
            encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": vision_model_name, # Use the dynamic vision_model_name here
            "prompt": "Describe this image in detail.",
            "stream": False,
            "images": [encoded_image]
        }
        print(f"\033[1;93m[UPLOAD]\033[0m Sending image to vision model '{vision_model_name}' at {ollama_url}...")
        response = requests.post(ollama_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        if 'response' in data:
            return data['response']
        else:
            # Provide more context if response field is missing
            return f"\033[91m[ERROR]\033[0m Ollama API response missing 'response' field. Full data: {data}"

    except requests.exceptions.ConnectionError:
        return f"\033[91m[ERROR]\033[0m Could not connect to Ollama at {ollama_url}. Is Ollama running and the '{vision_model_name}' model pulled?"
    except requests.exceptions.Timeout:
        return "\033[91m[ERROR]\033[0m Ollama request timed out. The image might be too large or processing is slow. Try a smaller image or increase timeout."
    except requests.exceptions.RequestException as e:
        return f"\033[91m[ERROR]\033[0m Error communicating with Ollama: {e}"
    except Exception as e:
        return f"\033[91m[ERROR]\033[0m An unexpected error occurred during image processing: {e}"