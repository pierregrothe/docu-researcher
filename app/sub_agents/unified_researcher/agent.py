from app.config import config
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.genai import types as genai_types
from google.adk.planners import BuiltInPlanner
from app import callbacks
from . import prompt

# This new agent combines the logic of both previous research agents.
unified_researcher = LlmAgent(
    model=config.lite_model,
    name="unified_researcher",
    description=(
        "Performs research on a knowledge node. If it's the first attempt, "
        "it does broad research. If the node has failed evaluation, it "
        "executes specific follow-up queries."
    ),
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=prompt.INSTRUCTION,
    tools=[google_search],
    output_key="node_research_results",
    # The same callback can be used as it just updates the brief.
    after_agent_callback=callbacks.update_brief_with_research_callback,
)