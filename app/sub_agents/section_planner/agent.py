from app.config import config

from google.adk.agents import LlmAgent
from google.genai import types as genai_types
from google.adk.planners import BuiltInPlanner

from app.schemas.brief import DocumentaryBrief
from app.callbacks import display_confirmation_callback
from . import prompt

section_planner = LlmAgent(
    model=config.lite_model,
    name="section_planner",
    description="Initializes the comprehensive DocumentaryBrief JSON structure from the approved research plan.",
    instruction=prompt.INSTRUCTION,
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    output_schema=DocumentaryBrief,
    output_key="documentary_brief",
    after_agent_callback=display_confirmation_callback,
)