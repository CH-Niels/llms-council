import sys
import asyncio
import time
import logging
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

from agent_factory import create_agents
from scripts.config_loader import load_config
from runner import run_pipeline
from scripts.validation.ollama_validation import ensure_ollama

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


async def main():
    try:

        ensure_ollama()

        cfg = load_config("configs/agents_config.yaml")
        agents = create_agents(cfg)
        
        task = str(input("Enter the task for the agents: "))

        decisionMaker_message, elapsed_time = await run_pipeline(task, agents, pipeline_order=cfg.get("pipeline", []))

        print(decisionMaker_message)
        print (f"Elapsed time: {elapsed_time:.2f} seconds")

        sys.exit(1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

asyncio.run(main())