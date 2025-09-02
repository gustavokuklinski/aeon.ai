# src/utils/load.py
import zipfile
from pathlib import Path
from src.config import MEMORY_DIR
from src.libs.messages import print_success_message, print_error_message


def loadBackup(zip_path: str, destination_path: Path):
    zip_file = Path(zip_path)
    destination_path = MEMORY_DIR
    
    if not zip_file.exists():
        print_error_message(f"Error: The file '{zip_path}' does not exist.")
        return False
    if not zipfile.is_zipfile(zip_file):
        print_error_message(f"Error: The file '{zip_path}' is not a valid zip archive.")
        return False
        
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(destination_path)
        print_success_message(f"Successfully unzipped '{zip_path}' to '{destination_path}'.")
        return True
    except Exception as e:
        print_error_message(f"An error occurred during unzipping: {e}")
        return False