from app.config import config
from . import prompt

# --- Correct ADK and GenAI imports ---
from google.adk.agents import LlmAgent

# Import the two schemas we will be working with
from app.schemas.brief import DocumentaryBrief


brief_finalizer = LlmAgent(
    model=config.worker_model,
    name="brief_finalizer",
    description="Assembles the final, complete DocumentaryBrief JSON object and constructs the knowledge graph.",
    instruction=prompt.INSTRUCTION,
    output_schema=DocumentaryBrief,
    output_key="final_documentary_brief",
)