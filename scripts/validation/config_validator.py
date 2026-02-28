import sys
import logging

# This module validates the configuration file for the agents.
# It ensures that all required fields are present and correctly formatted.

def validate_config(cfg):
    # Check if the 'agents' section exists in the configuration.
    if "agents" not in cfg:
        logging.error("Missing 'agents' section in config")
        sys.exit(1)

    # Validate the 'agents' section to ensure it is a non-empty dictionary.
    agents = cfg["agents"]
    if not isinstance(agents, dict) or not agents:
        logging.error("'agents' must be a non-empty dictionary")
        sys.exit(1)

    # Validate each agent's configuration.
    for key, agent in agents.items():
        if "group" not in agent or not agent["group"]:
            logging.error(f"Agent '{key}' missing 'group' field")
            sys.exit(1)
        if "name" not in agent or not agent["name"]:
            logging.error(f"Agent '{key}' missing 'name' field")
            sys.exit(1)
        if "system_message" not in agent or not agent["system_message"]:
            logging.error(f"Agent '{key}' missing 'system_message' field")
            sys.exit(1)
        if "llm_config" not in agent or "model" not in agent["llm_config"]:
            logging.error(f"Agent '{key}' missing 'llm_config.model'")
            sys.exit(1)

    # Validate the pipeline section to ensure it is a non-empty list.
    pipeline = cfg.get("pipeline", [])
    if not isinstance(pipeline, list) or not pipeline:
        logging.error("Pipeline must be a non-empty list of group names")
        sys.exit(1)

    # Check that all groups in the pipeline exist in the agents' configuration.
    agent_groups = {a["group"] for a in agents.values()}
    for group in pipeline:
        if group not in agent_groups:
            logging.error(f"Pipeline references group '{group}' which does not exist in agents")
            sys.exit(1)

    print("✅ Configuration validation passed")