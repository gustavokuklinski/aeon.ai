import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import importlib.util
from src.libs.messages import (
    print_error_message, print_info_message, print_success_message
)

# Define the base plugins directory relative to the project root
PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"


class Plugin:
    def __init__(self, name: str, config: Dict[str, Any], path: Path):
        self.name = name
        self.config = config
        self.path = path

        # Validate and set core plugin attributes from the config
        self.plugin_name = self.config.get('plugin_name', name)
        self.type = self.config.get('type')
        self.command = self.config.get('command')
        self.parameters = self.config.get('parameters')
        self.model_path = self.path / self.config.get('model_path', '')

        if not self.command:
            raise ValueError(
                f"Plugin '{name}' is missing a 'command' key in its config.")

        # Validate that the model path exists if one is specified
        if self.model_path and not self.model_path.exists():
            print_error_message(
                f"Model path for '{self.name}' not found: {self.model_path}")

    def get_parameters(self) -> Optional[str]:
        return self.parameters

    def __repr__(self):
        return f"Plugin(name='{self.plugin_name}', command='{self.command}', type='{self.type}')"

    def execute(self, *args, **kwargs) -> Optional[str]:
        try:
            main_file_path = self.path / "main.py"
            spec = importlib.util.spec_from_file_location(
                f"plugin.{self.name}", main_file_path
            )
            if spec is None:
                raise ImportError(
                    f"Could not create spec for plugin: {self.name}")

            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)

            if not hasattr(plugin_module, 'run_plugin'):
                print_error_message(
                    f"Plugin '{self.name}' is missing the 'run_plugin' function.")
                return None

            # Pass the plugin's config and path directly to the run_plugin function
            # This makes run_plugin more self-contained.
            return plugin_module.run_plugin(
                *args,
                plugin_config=self.config,
                plugin_dir=self.path,
                **kwargs
            )

        except Exception as e:
            print_error_message(
                f"An error occurred during plugin execution: {e}")
            return None


class PluginManager:
    def __init__(self, plugins_dir: Path = PLUGINS_DIR):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.load_plugins()

    def load_plugins(self):
        if not self.plugins_dir.exists():
            print_info_message(
                f"Warning: Plugins directory not found at {self.plugins_dir}")
            return

        self.plugins.clear()

        for plugin_path in self.plugins_dir.iterdir():
            if plugin_path.is_dir():
                config_path = plugin_path / "config.yml"
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            config_data = yaml.safe_load(f)
                            aeon_plugin_config = config_data.get('aeon_plugin')
                            if aeon_plugin_config:
                                # Instantiate Plugin with the parsed config data
                                plugin = Plugin(
                                    name=plugin_path.name,
                                    config=aeon_plugin_config,
                                    path=plugin_path
                                )
                                # Use the plugin's command as the dictionary key
                                self.plugins[plugin.command] = plugin
                                print_success_message(
                                    f"Plugin loaded: {plugin.name} (command: {plugin.command})")
                            else:
                                print_info_message(
                                    f"Skipping '{plugin_path.name}': 'aeon_plugin' key not found in config.")
                    except (yaml.YAMLError, ValueError) as e:
                        print_error_message(
                            f"Error loading config for '{plugin_path.name}': {e}")
                else:
                    print_info_message(
                        f"Skipping '{plugin_path.name}': config.yml not found.")

    def get_plugin(self, command: str) -> Optional[Plugin]:
        return self.plugins.get(command)

    def get_commands(self) -> list[str]:
        return list(self.plugins.keys())

    def execute_command(self, command: str, *args, **kwargs):
        plugin = self.get_plugin(command)
        if plugin:
            result = plugin.execute(*args, **kwargs)
            if result:
                print(result)
        else:
            print_error_message(f"No plugin found for command '{command}'.")
