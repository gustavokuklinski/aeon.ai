# src/web.py
import sys
from pathlib import Path
from flask import Flask

from src.config import OUTPUT_DIR, MEMORY_DIR
from src.webapp.routes import init_routes
from src.libs.messages import print_info_message

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

abs_output_dir = project_root / OUTPUT_DIR
abs_memory_dir = project_root / MEMORY_DIR

app = Flask(__name__,
            template_folder=str(project_root / 'web' / 'templates'),
            static_folder=str(project_root / 'web' / 'assets'))

init_routes(app, abs_output_dir, abs_memory_dir)

if __name__ == "__main__":
    print_info_message("Starting AEON web server...")
    app.run(host='0.0.0.0', debug=False, port=7860)
