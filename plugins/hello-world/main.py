# plugins/hello-world/main.py

from pathlib import Path

from src.libs.messages import (print_info_message, print_success_message,
                               print_error_message)

def run_plugin(*args, **kwargs) -> None:
    """
    Main function to execute the 'Hello World' plugin.
    This plugin simply echoes back the string provided by the user.
    
    Args:
        *args: Positional arguments provided by the user (expected to be a single string).
        **kwargs: Keyword arguments (e.g., 'plugin_config', 'plugin_dir').
        
    Returns:
        None: All output is handled directly via print_..._message functions.
    """
    plugin_config = kwargs.get('plugin_config')
    plugin_name = plugin_config.get("plugin_name", "Hello World Plugin") if plugin_config else "Hello World Plugin"

    if not args:
        print_error_message(f"Usage: /hello <PROMPT>")
        return

    user_string = args[0]
    
    print_info_message(f"'{plugin_name}' received input: '{user_string}'")
    print_success_message(f"Hello, you said: {user_string}")
    
    return None