import json
import sys
import os
from langchain_core.documents import Document

class JsonPlaintextLoader:
    def __init__(self, file_path: str): # Removed hide_messages parameter
        self.file_path = file_path

    def _print_info_line(self, message: str):
        """
        Prints a single info line to the console.
        """
        terminal_width = 80
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            pass

        info_line = f"\033[1;34m[INFO]\033[0m {message}"
        print(info_line.ljust(terminal_width))
        sys.stdout.flush()

    def _count_string_nodes(self, obj) -> int:
        """
        Recursively counts the total number of string nodes within a JSON object.
        """
        count = 0
        if isinstance(obj, dict):
            for v in obj.values():
                count += self._count_string_nodes(v)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_string_nodes(item)
        elif isinstance(obj, str):
            count += 1
        return count

    def load(self) -> list[Document]:
        """
        Loads the JSON file, extracts all string values, and returns them as a list of Document objects.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            documents = []
            total_string_nodes = self._count_string_nodes(data)
            processed_string_nodes = 0

            def _extract_strings_recursively(obj, current_path=""):
                nonlocal processed_string_nodes
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        _extract_strings_recursively(v, f"{current_path}.{k}" if current_path else k)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        _extract_strings_recursively(item, f"{current_path}[{i}]" if current_path else str(i))
                elif isinstance(obj, str):
                    documents.append(Document(
                        page_content=obj,
                        metadata={
                            "source": self.file_path,
                            "json_path": current_path,
                            "file_type": "json_plaintext"
                        }
                    ))
                    processed_string_nodes += 1

            _extract_strings_recursively(data)

            print() # Print a final newline for cleaner output

            if not documents:
                print(f"\033[1;33m[WARN]\033[0m No string content found in '{self.file_path}'.")

            return documents

        except json.JSONDecodeError as e:
            # Errors are critical, always print
            print(f"\033[91m[ERROR]\033[0m Invalid JSON file '{self.file_path}': {e}")
            return []
        except FileNotFoundError:
            # Errors are critical, always print
            print(f"\033[91m[ERROR]\033[0m File not found: '{self.file_path}'")
            return []
        except Exception as e:
            # Errors are critical, always print
            print(f"\033[91m[ERROR]\033[0m Error loading JSON file '{self.file_path}': {e}")
            return []