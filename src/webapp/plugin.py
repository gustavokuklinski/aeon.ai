import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from src.libs.plugins import PluginManager, PLUGINS_DIR
from src.libs.messages import print_info_message

_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager(plugins_dir: Path = PLUGINS_DIR) -> PluginManager:
    global _plugin_manager
    if _plugin_manager is None:
        # Find all subdirectories in the PLUGINS_DIR to load
        plugin_names = [d.name for d in plugins_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        _plugin_manager = PluginManager(plugins_to_load=plugin_names, plugins_dir=plugins_dir)
        print_info_message(f"Plugins loaded: {list(_plugin_manager.plugins.keys())}")
    return _plugin_manager

def handle_plugin_command(
    user_input: str,
    conv_id: str,
    current_memory_path: Path,
    rag_system_vars: Dict[str, Any]
) -> Tuple[bool, str, str]:
    manager = get_plugin_manager()
    parts = user_input.split(' ', 1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    plugin = manager.plugins.get(command)

    if plugin:
        if not current_memory_path:
            return True, "Internal Error: The conversation memory path is missing. Cannot run plugin.", f"Plugin: {plugin.plugin_name}"
       
        output_dir = current_memory_path / 'outputs'
        os.makedirs(output_dir, exist_ok=True)

        print(f"[PLUGIN] Executing command '{command}' with args: '{args}'")
        
        rag_vars_for_plugin = rag_system_vars.copy()
        rag_vars_for_plugin.pop("current_memory_path", None)
        rag_vars_for_plugin.pop("current_conversation_id", None)
        rag_vars_for_plugin.pop("conversation_filename", None)

        plugin_result = plugin.execute(
            args,
            output_dir=output_dir,
            current_memory_path=current_memory_path, 
            conversation_id=conv_id,
            conversation_filename=f"{conv_id}.json",
            **rag_vars_for_plugin
        )

        if isinstance(plugin_result, dict):
            message = plugin_result.get('message', f"Plugin {command} executed but returned no message.")
            source = plugin_result.get('source', f"Plugin: {plugin.plugin_name}")
            
            if 'filepath' in plugin_result:
                filepath_value = plugin_result['filepath']
                if filepath_value:
                    try:
                        relative_filepath = Path(filepath_value).relative_to(current_memory_path)
                        file_url = f"/serve_from_memory/{relative_filepath.as_posix()}?conv_id={conv_id}" 
                        if plugin.type == 'text-image':
                            message = f"{message}\n\n![Generated File]({file_url})"
                        elif plugin.type == 'text-audio':
                            message = f"{message}\n\n<audio controls><source src='{file_url}' type='audio/wav'></audio>"

                    except Exception as e:
                        print(f"[PLUGIN WARNING] Could not resolve filepath for {plugin.plugin_name}: {e}")
                else:
                    print(f"[PLUGIN INFO] Plugin {plugin.plugin_name} returned None for filepath")
            
            return True, message, source
        
        elif plugin_result is None:
            return True, f"Plugin '{command}' executed successfully but returned no output.", f"Plugin: {plugin.plugin_name}"
        

        return True, str(plugin_result), f"Plugin: {plugin.plugin_name}"
    
    return False, "", ""
