from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types

from app.config import config

from app import callbacks
from . import prompt

enhanced_search_executor = LlmAgent(
    model=config.lite_model,
    name="enhanced_search_executor",
    description="Executes targeted follow-up searches to fill narrative gaps identified by the evaluator.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=prompt.INSTRUCTION,
    tools=[google_search],
    output_key="node_research_results",
    after_agent_callback=callbacks.update_brief_with_research_callback,
)