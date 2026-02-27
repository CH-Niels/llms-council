import yaml
import asyncio
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
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

# Assign agents
planner = agents["planner"]
experts = [agents["expert1"], agents["expert2"]]
critics = [agents["critic1"], agents["critic2"]]
judge = agents["judge"]

# Council Manager
class CouncilManager:
    def __init__(self, planner, experts, critics, judge):
        self.planner = planner
        self.experts = experts
        self.critics = critics
        self.judge = judge
        self.conversation_history = []
        self.turn_counts = {}  # Track turns per agent
        self.previous_speaker = None
    
    async def run_agent_turn(self, agent, context):
        """Run a single agent turn and collect the response"""
        print(f"\n=== {agent.name} ===")
        result = await agent.run(task=context)
        response = result.messages[-1].content if result.messages else ""
        print(f"{response}\n")
        self.conversation_history.append(f"{agent.name}: {response}")
        self.previous_speaker = agent.name
        
        # Track turn count
        self.turn_counts[agent.name] = self.turn_counts.get(agent.name, 0) + 1
        
        return response
    
    def get_available_agents(self, stage):
        """Get agents that haven't reached their turn limit for the current stage"""
        if stage == "experts":
            available = [e for e in self.experts if self.turn_counts.get(e.name, 0) < 2]
        elif stage == "critics":
            available = [c for c in self.critics if self.turn_counts.get(c.name, 0) < 2]
        else:
            return []
        
        # Filter out previous speaker to avoid consecutive turns
        if self.previous_speaker:
            available = [a for a in available if a.name != self.previous_speaker]
        
        return available
    
    async def run(self, task):
        """Run the full council process with controlled turns"""
        self.conversation_history = [f"Task: {task}"]
        self.turn_counts = {}
        self.previous_speaker = None
        
        # Planner turn
        context = task
        await self.run_agent_turn(self.planner, context)
        
        # Experts - 2 turns each, alternating
        while any(self.turn_counts.get(e.name, 0) < 2 for e in self.experts):
            available = self.get_available_agents("experts")
            if not available:
                # If only previous speaker left, allow them
                available = [e for e in self.experts if self.turn_counts.get(e.name, 0) < 2]
            if available:
                expert = available[0]  # Pick first available
                context = "\n\n".join(self.conversation_history)
                await self.run_agent_turn(expert, context)
        
        # Critics - 2 turns each, alternating
        while any(self.turn_counts.get(c.name, 0) < 2 for c in self.critics):
            available = self.get_available_agents("critics")
            if not available:
                # If only previous speaker left, allow them
                available = [c for c in self.critics if self.turn_counts.get(c.name, 0) < 2]
            if available:
                critic = available[0]  # Pick first available
                context = "\n\n".join(self.conversation_history)
                await self.run_agent_turn(critic, context)
        
        # Judge final decision
        context = "\n\n".join(self.conversation_history)
        final_response = await self.run_agent_turn(self.judge, context)
        
        return final_response

# Run chat asynchronously
async def main():
    task = str(input("Enter the task for the agents: "))
    
    manager = CouncilManager(planner, experts, critics, judge)
    final_decision = await manager.run(task)
    
    print(f"\n{'='*60}")
    print(f"FINAL DECISION: {final_decision}")
    print(f"{'='*60}")


asyncio.run(main())