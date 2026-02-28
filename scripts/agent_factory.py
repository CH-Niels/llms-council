from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

# This module is responsible for creating agents based on the configuration.

def create_agents(cfg):
    # Initialize an empty dictionary to store the agents.
    agents = {}

    # Extract the basic LLM settings from the configuration.
    llm_basic = cfg["llm_basic_settings"]

    # Iterate through each agent's configuration and create the agent.
    for key, agent_cfg in cfg["agents"].items():
        # Merge the basic LLM settings with the agent-specific configuration.
        llm_cfg = {
            "model": agent_cfg["llm_config"]["model"],
            "temperature": agent_cfg["llm_config"].get("temperature", 0.7),
            "base_url": llm_basic["base_url"],
            "api_key": llm_basic["api_key"],
            "model_info": llm_basic["model_info"].copy()
        }

        # Create the model client using the merged configuration.
        model_client = OllamaChatCompletionClient(**llm_cfg)

        # Create the agent and assign it to the agents dictionary.
        agents[key] = AssistantAgent(
            name=agent_cfg["name"],
            system_message=agent_cfg["system_message"],
            model_client=model_client
        )
        # Assign the group to the agent for pipeline execution.
        agents[key].group = agent_cfg["group"]

    # Return the dictionary of created agents.
    return agents