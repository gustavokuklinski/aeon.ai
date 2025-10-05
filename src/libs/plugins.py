import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import importlib.util
from src.libs.messages import (
    print_error_message, print_info_message, print_plugin_message
)

PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"


class Plugin:
    def __init__(self, name: str, config: Dict[str, Any], path: Path):
        self.name = name
        self.config = config
        self.path = path

        self.plugin_name = self.config.get('plugin_name', name)
        self.type = self.config.get('type')
        self.command = self.config.get('command')
        self.parameters = self.config.get('parameters')
        self.desc = self.config.get('desc')
        self.model_path = self.path / self.config.get('model_path', '')

        if not self.command:
            raise ValueError(
                f"Plugin '{name}' is missing a 'command' key in its config.")

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
    def __init__(self, plugins_to_load: list[str], plugins_dir: Path = PLUGINS_DIR):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.plugins_to_load = plugins_to_load
        self.load_plugins()

    def list_plugins(self):
        """
        Returns a list of all currently loaded plugins' metadata, formatted for the frontend.
        The list contains dictionaries like [{'name': command, 'description': desc}].
        """
        # FIX: Correctly iterate over the loaded plugins dictionary (self.plugins)
        plugin_list = []
        for plugin in self.plugins.values():
            plugin_list.append({
                # Use command as the unique identifier/name for the frontend command
                'name': plugin.command,
                'parameters': plugin.parameters,
                'description': plugin.desc # Use desc as the description
            })

        print_plugin_message(f"Listing {len(self.plugins)} loaded plugins.")
        return plugin_list

    def load_plugins(self):
        if not self.plugins_dir.exists():
            print_info_message(
                f"Warning: Plugins directory not found at {self.plugins_dir}")
            return

        self.plugins.clear()

        for plugin_name in self.plugins_to_load:
            plugin_path = self.plugins_dir / plugin_name
            config_path = plugin_path / "config.yml"

            if not plugin_path.is_dir() or not config_path.exists():
                print_error_message(f"Skipping '{plugin_name}': Not a valid plugin directory or config.yml not found.")
                continue

            try:
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    aeon_plugin_config = config_data.get('aeon_plugin')
                    if aeon_plugin_config:
                        plugin = Plugin(
                            name=plugin_name,
                            config=aeon_plugin_config,
                            path=plugin_path
                        )

                        self.plugins[plugin.command] = plugin
                    else:
                        print_info_message(
                            f"Skipping '{plugin_name}': 'aeon_plugin' key not found in config.")
            except (yaml.YAMLError, ValueError) as e:
                print_error_message(
                    f"Error loading config for '{plugin_name}': {e}")
