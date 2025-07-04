from app.config import config

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from .prompt import INSTRUCTION

context_researcher = LlmAgent(
    model=config.lite_model,
    name="context_researcher",
    description="Clarifies ambiguous topics by performing a web search.",
    instruction=INSTRUCTION,
    tools=[google_search], # This agent can use tools.
)