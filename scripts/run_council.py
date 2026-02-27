import yaml
import asyncio
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.ui import Console

from check_ollama import ensure_ollama

ensure_ollama()

# Load YAML
with open("configs/agents_config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

llm_basic = cfg["llm_basic_settings"]
agents_cfg = cfg["agents"]

agents = {}

for key, agent_cfg in agents_cfg.items():
    # Merge basic LLM settings with agent-specific config
    llm_cfg = {
        "model": agent_cfg["llm_config"]["model"],
        "temperature": agent_cfg["llm_config"].get("temperature", 0.7),
        "base_url": llm_basic["base_url"],
        "api_key": llm_basic["api_key"],
        "model_info": llm_basic["model_info"].copy()
    }

    # Create Ollama client dynamically
    model_client = OllamaChatCompletionClient(
        model=llm_cfg["model"],
        base_url=llm_cfg["base_url"],
        api_key=llm_cfg["api_key"],
        temperature=llm_cfg["temperature"],
        model_info=llm_cfg["model_info"]
    )

    # Create the agent
    agents[key] = AssistantAgent(
        name=agent_cfg["name"],
        system_message=agent_cfg["system_message"],
        model_client=model_client
    )

# Termination condition
termination = MaxMessageTermination(10)

# Create group chat team
group_chat = RoundRobinGroupChat(
    participants=list(agents.values()),
    termination_condition=termination,
)

# Run chat asynchronously
async def main():

    task = str(input("Enter the task for the agents: "))
    stream = group_chat.run_stream(task=task)
    await Console(stream)

asyncio.run(main())