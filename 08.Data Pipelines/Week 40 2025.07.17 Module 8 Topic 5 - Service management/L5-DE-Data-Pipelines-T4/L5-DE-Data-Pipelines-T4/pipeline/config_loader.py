# pipeline/config_loader.py

import json
import os

def load_json_config(filename):
    """
    Load a JSON config file from the project-level 'config' directory,
    no matter where this module is run from.
    """
    # Get the absolute path to the 'config' directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, 'config', filename)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)