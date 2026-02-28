# This module handles loading the agents' configuration from a YAML file.

import yaml
import logging
import sys

def load_agents_config(path: str):
    # Attempt to load the YAML configuration file.
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Log an error if the file is not found and exit the program.
        logging.error(f"Configuration file not found: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        # Log an error if there is an issue parsing the YAML file and exit the program.
        logging.error(f"Error parsing YAML configuration: {e}")
        sys.exit(1)