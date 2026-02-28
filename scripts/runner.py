import logging
import time
from autogen_agentchat.teams import RoundRobinGroupChat
from collections import defaultdict
from autogen_agentchat.conditions import MaxMessageTermination
from utils import collect_results, save_full_discussion

# This module handles the execution of the agent pipeline.
# It runs tasks through groups of agents in the specified pipeline order.

async def run_pipeline(task, agents, pipeline_order, termination_count=9):
    start_time = time.time()

    # Group agents by their 'group' field for pipeline execution.
    grouped_agents = defaultdict(list)
    for agent in agents.values():
        grouped_agents[agent.group].append(agent)

    current_input = task
    outputs = {}  # Store outputs for each group.

    # Iterate through each group in the pipeline order.
    for group_name in pipeline_order:
        group_members = grouped_agents.get(group_name, [])
        if not group_members:
            print(f"⚠️  No agents in group '{group_name}', skipping...")
            continue

        print(f"\n⚙️  Running group: {group_name} ({len(group_members)} agent(s))")

        # If there is only one agent in the group, run it directly.
        if len(group_members) == 1:
            agent = group_members[0]
            result = await agent.run(task=current_input, output_task_messages=False)
            output = collect_results(result.messages)

        # If there are multiple agents, use a RoundRobinGroupChat.
        else:
            team = RoundRobinGroupChat(
                name=f"{group_name} group",
                participants=group_members,
                termination_condition=MaxMessageTermination(termination_count)
            )
            result = await team.run(task=current_input, output_task_messages=False)
            output = collect_results(result.messages)

        # Store the output of the current group.
        outputs[group_name] = output
        # Pass the output to the next group in the pipeline.
        current_input = output
    elapsed_time = time.time() - start_time

    # Save everything
    save_full_discussion(
        task=task,
        group_outputs=outputs,
        elapsed_time=elapsed_time
    )
    
    return outputs.get(pipeline_order[-1], ""), elapsed_time