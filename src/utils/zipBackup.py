# src/utils/zip.py
import os
import shutil
from datetime import datetime
from pathlib import Path

from src.utils.messages import *

def zipBackup(source_dir, output_dir):

    try:
        # Resolve paths to ensure they are absolute and correctly formatted
        project_root = Path(__file__).parent.parent.parent
        source_path = project_root / source_dir
        output_path = project_root / output_dir / "backup"
        
        # Ensure the output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create a timestamped filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        zip_filename_base = f"memory_{timestamp}"
        
        print(f"Creating zip backup of '{source_path}'...")
        
        # Use shutil.make_archive to create the zip file
        archive_path = shutil.make_archive(
            base_name=str(output_path / zip_filename_base),
            format='zip',
            root_dir=str(source_path)
        )
        
        print(f"Backup successfully created at: {archive_path}")
        return archive_path
        
    except FileNotFoundError:
        print(f"Error: The source directory '{source_dir}' does not exist.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during zipping: {e}")
        return None

if __name__ == '__main__':
    # This block allows you to test the function independently
    # Note: Adjust the paths as necessary for your project structure
    from src.config import MEMORY_DIR, OUTPUT_DIR

    create_zip_backup(MEMORY_DIR, OUTPUT_DIR)