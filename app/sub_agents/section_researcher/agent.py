from app.config import config

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.genai import types as genai_types
from google.adk.planners import BuiltInPlanner

from app import callbacks
from . import prompt

section_researcher = LlmAgent(
    model=config.lite_model,
    name="section_researcher",
    description="Performs the initial source discovery and fact extraction for a single knowledge node.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=prompt.INSTRUCTION,
    tools=[google_search],
    output_key="node_research_results",
    after_agent_callback=callbacks.update_brief_with_research_callback,
)