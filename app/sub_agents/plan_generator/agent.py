# app/sub_agents/plan_generator/agent.py
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types as genai_types
from google.adk.planners import BuiltInPlanner
from app.config import config

# Import the corrected schema that includes search_queries
from app.schemas.narrative import NarrativePlan

from . import prompt
from app.sub_agents.context_researcher.agent import context_researcher

# Define the Planner Agent: This agent takes text and outputs JSON. It has no tools.
planner_agent = LlmAgent(
    model=config.critic_model,
    name="planner_agent",
    description="Takes research context and creates a structured JSON narrative plan.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=prompt.INSTRUCTION,
    output_schema=NarrativePlan, # It outputs structured JSON.
)

# Define the Plan Generator Tool: This is a SequentialAgent that acts as a single tool.
# It runs the researcher first, then pipes the output to the planner.
plan_generator = SequentialAgent(
    name="plan_generator",
    description="A tool that first clarifies a topic, then generates a comprehensive JSON research plan.",
    sub_agents=[
        context_researcher,
        planner_agent,
    ]
)