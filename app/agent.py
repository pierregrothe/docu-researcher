import logging

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.graph import BuiltInPlanner
from google.adk.graph import genai_types

from .config import config
from . import prompt
from . import callbacks

# --- Import our new, modular sub-agent ---
from .sub_agents.research_pipeline.agent import research_pipeline
from .sub_agents.plan_generator.agent import plan_generator
#from .sub_agents.brief_initializer.agent import BriefInitializerAgent
# --- Corrected Imports to add at the top of app/agent.py ---

# Add these three lines to enable detailed API tracing.
# This will print all requests and responses from the Google API client.
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("google.api_core").setLevel(logging.DEBUG)
logging.getLogger("google.auth").setLevel(logging.DEBUG)

# --- AGENT DEFINITIONS ---
interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model=config.worker_model,
    description="A simple routing agent that presents a plan for user approval.",
    instruction=prompt.INSTRUCTION,
    sub_agents=[research_pipeline],
    tools=[AgentTool(plan_generator)],
    after_agent_callback=callbacks.save_plan_to_state_callback,
    verbose=True,
    max_execution_turns=10,
    planner=BuiltInPlanner(thinking_config=genai_types.ThinkingConfig(include_thoughts=True)),
)

root_agent = interactive_planner_agent
