from app.config import config

from google.adk.agents import LlmAgent

from app.schemas.brief import Feedback
from . import prompt

research_evaluator = LlmAgent(
    model=config.critic_model,
    name="research_evaluator",
    description="Critiques the fact collection for a node and checks for research saturation.",
    instruction=prompt.INSTRUCTION,
    output_schema=Feedback,
    output_key="research_evaluation",
)