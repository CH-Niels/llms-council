import yaml
import asyncio
import os
import time
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
termination = MaxMessageTermination(9)


# Assign stages
planner = agents["planner"]
experts = [agents["expert1"], agents["expert2"]]
critics = [agents["critic1"], agents["critic2"]]
decisionMaker = agents["decisionMaker"]

# Create group chat team
group_chat = RoundRobinGroupChat(
    name="Expert-Critic Discussion",
    description="A discussion between experts and critics to evaluate the planner's solution.",
    participants=[*experts, *critics],
    termination_condition=termination
)

# Helper function to collect results from the group chat run
def collect_results(messages):
    transcript_lines = []
    for msg in messages:
        transcript_lines.append(f"Source: {msg.source}\nContent: {msg.content}")
    transcript = "\n\n".join(transcript_lines)
    return transcript

# Helper function to save the entire discussion (planner, experts, critics, and decisionMaker) to a single file
def save_full_discussion(task, planner_result, transcript, decisionMaker_result, elapsed_time, folder="logs"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, f"{time.time().__str__().replace('.', '')}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("=== Task ===\n\n")
        f.write(task + "\n\n")
        f.write("=== Planner ===\n\n")
        f.write(planner_result + "\n\n")
        f.write("=== Discussion (Experts and Critics) ===\n\n")
        f.write(transcript + "\n\n")
        f.write("=== DecisionMaker ===\n\n")
        f.write(decisionMaker_result + "\n\n")
        f.write(f"=== Elapsed Time ===\n\n{elapsed_time:.2f} seconds\n")
    print(f"Full discussion log saved to {file_path}")

# Run chat asynchronously
async def main():
    task = str(input("Enter the task for the agents: "))

    start_time = time.time()  # Start the timer
    print("🚀 Running the planner agent...")
    
    result_planner = await planner.run(task=task)
    planner_message = result_planner.messages[-1].content
    
    print("🚀 Running the discussion group chat...")

    result_discussion = await group_chat.run(task=planner_message, output_task_messages=False)  # Await the coroutine
    transcript = collect_results(result_discussion.messages)

    if not transcript.strip():
        print("Warning: Transcript is empty. Check if agents are responding correctly.")

    print("🚀 Running the decision maker agent...")

    result_decisionMaker = await decisionMaker.run(task=f"Task: {task}\nExperts' transcript: {transcript}\n", output_task_messages=False)
    decisionMaker_message = result_decisionMaker.messages[-1].content

    print(decisionMaker_message)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time

    print (f"Elapsed time: {elapsed_time:.2f} seconds")

    # Save the entire discussion to a single file
    save_full_discussion(task, planner_message, transcript, decisionMaker_message, elapsed_time)


asyncio.run(main())