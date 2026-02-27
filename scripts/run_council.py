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
termination = MaxMessageTermination(6)


# Assign stages
planner = agents["planner"]
experts = [agents["expert1"], agents["expert2"]]
critics = [agents["critic1"], agents["critic2"]]
judge = agents["judge"]

# Create group chat team
group_chat_experts = RoundRobinGroupChat(
    participants=experts,
    termination_condition=termination,
)

group_chat_critics = RoundRobinGroupChat(
    participants=critics,
    termination_condition=termination,
)

# Helper function to stream messages and collect results
async def stream_and_collect(stream):
    """Stream messages to console and collect the final result and transcript"""
    messages = []
    transcript_lines = []
    async for message in stream:
        print(message)
        messages.append(message)
        content = message.content if hasattr(message, "content") else str(message)
        transcript_lines.append(content)
    last_msg = messages[-1] if messages else None
    last_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg) if last_msg else ""
    transcript = "\n\n".join(transcript_lines)
    return last_content, transcript

# Run chat asynchronously
async def main():
    task = str(input("Enter the task for the agents: "))

    print("=== Planner ===")
    result_planner = await planner.run(task=task)
    print(result_planner.messages[-1].content)
    planner_content = result_planner.messages[-1].content
    
    print("=== Experts ===")
    stream_experts = group_chat_experts.run_stream(task=planner_content)
    experts_content, experts_transcript = await stream_and_collect(stream_experts)
    print(f"\nExperts final response: {experts_content}\n")
    
    print("=== Critics ===")
    critics_task = (
        "Critique the experts' reasoning process and final answer.\n\n"
        f"Experts full transcript:\n{experts_transcript}\n\n"
        f"Experts final answer:\n{experts_content}"
    )
    stream_critics = group_chat_critics.run_stream(task=critics_task)
    critics_content, critics_transcript = await stream_and_collect(stream_critics)
    print(f"\nCritics final response: {critics_content}\n")
    
    print("=== Judge ===")
    result_judge = await judge.run_stream(task=f"Task: {task}\nExperts' solution: {experts_content}\nCritics' feedback: {critics_content}")
    await Console(result_judge)


asyncio.run(main())