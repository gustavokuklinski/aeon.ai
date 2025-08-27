# src/libs/zip.py
import shutil
from datetime import datetime
from pathlib import Path

from src.libs.messages import (print_info_message,
                               print_success_message, print_error_message)


def zipBackup(source_dir: Path, output_dir: str):

    try:
        project_root = Path(__file__).parent.parent.parent
        source_path = project_root / source_dir
        output_path = project_root / output_dir / "backup"

        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        zip_filename_base = f"memory_{timestamp}"

        print_info_message(f"Creating zip backup of '{source_path}'...")

        archive_path = shutil.make_archive(
            base_name=str(output_path / zip_filename_base),
            format='zip',
            root_dir=str(source_path)
        )

        print_success_message("Backup successfully "
                              f"created at: {archive_path}")
        return archive_path

    except FileNotFoundError:
        print_error_message("Error: The source directory "
                            f"'{source_dir}' does not exist.")
        return None
    except Exception as e:
        print_error_message("An unexpected error "
                            f"occurred during zipping: {e}")
        return None
