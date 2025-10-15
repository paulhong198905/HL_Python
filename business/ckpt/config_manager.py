# business/ckpt/config_manager.py

from typing import Dict, Any

import yaml


# --- Custom Exception ---
class ConfigurationError(Exception):
    """Custom exception for configuration loading and parsing errors."""
    pass


class ConfigManager:
    """Manages loading and merging configuration data from YAML files."""

    def __init__(self, pn_map_path: str = 'config/pn_map.yaml'):
        self.pn_map_path = pn_map_path
        # The keys in self.pn_map_data['part_numbers'] will be strings, e.g., '36666666'
        self.pn_map_data: Dict[str, Any] = self._load_yaml(self.pn_map_path)

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Loads a YAML file from disk."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing YAML file {file_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"An unexpected error occurred loading {file_path}: {e}")

    def is_pn_valid(self, pn: str) -> bool:
        """Checks if the Part Number (as a string) exists in the loaded map."""
        if not self.pn_map_data or 'part_numbers' not in self.pn_map_data:
            raise ConfigurationError("PN map data is missing or improperly structured.")

        # Check for the string key '36666666' in the map
        return pn in self.pn_map_data.get('part_numbers', {})

    # --- PHASE 1: Quick Lookup ---
    def get_program_name(self, pn: str) -> str:
        """Quickly retrieves only the program name for immediate display."""
        if not self.is_pn_valid(pn):
            raise ConfigurationError(f"PN '{pn}' not found in map.")

        filenames_map = self.pn_map_data['part_numbers'][pn]

        # Note: program_name value is expected to be a string, e.g., "U557 NS-1"
        program_name = filenames_map.get('program_name', 'UNKNOWN_PROGRAM_KEY_MISSING')

        return program_name

    # --- PHASE 2: Heavy Load (Deferred until Start button click) ---
    def get_pn_config_filenames(self, pn: str) -> Dict[str, str]:
        """Retrieves the dictionary of configuration file names associated with the PN."""
        if not self.is_pn_valid(pn):
            raise ConfigurationError(f"PN '{pn}' not found in map.")
        return self.pn_map_data['part_numbers'][pn]
    #
    # def load_and_merge_config_data(self, filenames_map: Dict[str, Any]) -> Dict[str, Any]:
    #     """Loads the content of all associated YAML files and merges them."""
    #
    #     program_name = filenames_map.get('program_name', 'UNKNOWN_PROGRAM_KEY_MISSING')
    #
    #     # Start the merged config with essential PN info from the map
    #     merged_config = {
    #         'pn': self.current_pn_config.get('pn'),  # Get the raw PN string
    #         'description': filenames_map.get('description', 'No Description'),
    #         'program_name': program_name
    #     }
    #
    #     print(f"ConfigManager: Starting heavy load for {program_name}...")
    #
    #     # Load the content of other files referenced in the map
    #     # Now handles the new keys: diag_config_file, can_decode_file
    #     for key, filename in filenames_map.items():
    #         # Skip program_name and description, as they are already handled
    #         if key in ['program_name', 'description'] or not isinstance(filename, str) or not filename.endswith(
    #                 '.yaml'):
    #             continue
    #
    #         try:
    #             # Dynamically determine the destination key name (e.g., 'wh_config_file' -> 'wh_config_data')
    #             data_key = key.replace('_file', '_data')
    #             file_data = self._load_yaml(f"config/{filename}")  # Assuming files are in a 'config/' folder
    #             merged_config[data_key] = file_data
    #             print(f"ConfigManager: Successfully loaded {filename}")
    #         except ConfigurationError as e:
    #             print(f"WARNING: Could not load required file {filename}. Error: {e}")
    #
    #     return merged_config
