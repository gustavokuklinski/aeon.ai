# src/libs/zip.py
import os
import shutil
from datetime import datetime
from pathlib import Path

from src.libs.messages import *

def zipBackup(source_dir: Path, output_dir: str):

    try:
        project_root = Path(__file__).parent.parent.parent
        source_path = project_root / source_dir
        output_path = project_root / output_dir / "backup"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        zip_filename_base = f"memory_{timestamp}"
        
        print(f"Creating zip backup of '{source_path}'...")
        
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
