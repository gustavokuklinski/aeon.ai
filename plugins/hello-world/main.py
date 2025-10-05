# plugins/hello-world/main.py

from pathlib import Path

from src.libs.messages import (print_info_message, print_success_message,
                               print_error_message)

def run_plugin(*args, **kwargs) -> None:
    plugin_config = kwargs.get('plugin_config')
    plugin_name = plugin_config.get("plugin_name")

    if not args:
        print_error_message(f"Usage: /hello <PROMPT>")
        return

    user_string = args[0]
    
    print_info_message(f"'{plugin_name}' received input: '{user_string}'")
    print_success_message(f"Hello, you said: {user_string}")
    
    return {
        "plugin_name": plugin_name,
        "response": user_string,
        "status": "success"
    }