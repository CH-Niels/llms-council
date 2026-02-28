import sys
import asyncio
import logging

from agent_factory import create_agents
from config_loader import load_agents_config
from validation.config_validator import validate_config
from runner import run_pipeline
from validation.ollama_validation import ensure_ollama

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


# This is the main entry point for the application.
# It initializes the agents, validates the configuration, and runs the pipeline.

async def main():
    try:
        # Ensure the Ollama service is running and models are available.
        ensure_ollama()

        # Load and validate the agents' configuration.
        cfg = load_agents_config("configs/agents_config.yaml")
        validate_config(cfg)

        # Create agents based on the configuration.
        agents = create_agents(cfg)

        # Prompt the user to enter a task for the agents.
        task = str(input("Enter the task for the agents: "))

        # Run the pipeline with the specified task and configuration.
        decisionMaker_message, elapsed_time = await run_pipeline(task, agents, pipeline_order=cfg.get("pipeline", []))

        # Display the final decision and elapsed time.
        print(decisionMaker_message)
        print (f"Elapsed time: {elapsed_time:.2f} seconds")

        sys.exit(0)

    except Exception as e:
        # Log any unexpected errors and exit the program.
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

# Run the main function asynchronously.
asyncio.run(main())