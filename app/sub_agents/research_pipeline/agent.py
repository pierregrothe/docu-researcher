import logging
from collections.abc import AsyncGenerator

from google.adk.agents import SequentialAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import ValidationError

from app.schemas.brief import DocumentaryBrief, ResearchStatus
from app.sub_agents.section_planner.agent import section_planner
# Import the new unified researcher
from app.sub_agents.unified_researcher.agent import unified_researcher
from app.sub_agents.research_evaluator.agent import research_evaluator
from app.sub_agents.brief_finalizer.agent import brief_finalizer

# --- AGENT DEFINITIONS ---

class LoopConfigAgent(BaseAgent):
    """
    Sets the max_iterations for the refinement loop dynamically based on the
    number of knowledge nodes in the research plan.
    """
    def __init__(self, loop_agent: LoopAgent, name: str = "loop_config_agent"):
        super().__init__(name=name)
        self._loop_agent = loop_agent

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        brief_data = ctx.session.state.get("documentary_brief")
        if not brief_data:
            logging.warning(f"[{self.name}] 'documentary_brief' not found. Using default loop iterations.")
            yield Event(author=self.name)
            return

        try:
            brief = DocumentaryBrief.model_validate(brief_data)
            num_nodes = len(brief.knowledge_nodes)
            # Allow up to 3 passes per node as a generous buffer.
            new_max_iterations = num_nodes * 3
            self._loop_agent.max_iterations = new_max_iterations
            logging.info(f"[{self.name}] Dynamically set max_iterations to {new_max_iterations} for {num_nodes} nodes.")
        except Exception as e:
            logging.error(f"[{self.name}] Failed to set loop iterations: {e}")
        
        yield Event(author=self.name)


class EscalationChecker(BaseAgent):
    """
    Checks if all research nodes are complete. If they are, it escalates to
    stop the loop. It also updates the status of the last-evaluated node.
    """
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        brief_data = ctx.session.state.get("documentary_brief")
        evaluation = ctx.session.state.get("research_evaluation")

        if not brief_data:
            logging.warning(f"[{self.name}] Brief not found. Cannot check for completion.")
            yield Event(author=self.name)
            return

        try:
            brief = DocumentaryBrief.model_validate(brief_data)
        except ValidationError as e:
            logging.error(f"[{self.name}] Could not validate documentary_brief: {e}")
            yield Event(author=self.name)
            return

        # Update the status of the just-evaluated node, if there was an evaluation
        if evaluation:
            for node in brief.knowledge_nodes:
                if node.research_status == ResearchStatus.ACTIVE:
                    if evaluation.get("grade") == "pass":
                        node.research_status = ResearchStatus.SATURATED
                        logging.info(f"[{self.name}] Node '{node.node_title}' marked as SATURATED.")
                    else:
                        logging.info(f"[{self.name}] Node '{node.node_title}' remains ACTIVE for refinement.")
                    break

        all_nodes_complete = all(
            node.research_status in [ResearchStatus.SATURATED, ResearchStatus.STALLED]
            for node in brief.knowledge_nodes
        )

        ctx.session.state["documentary_brief"] = brief

        if all_nodes_complete:
            logging.info(f"[{self.name}] All research nodes are complete. Escalating to stop loop.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(f"[{self.name}] Research nodes still pending. Loop will continue.")
            yield Event(author=self.name)

# Define the LoopAgent instance so we can pass it to the config agent.
iterative_refinement_loop = LoopAgent(
    name="iterative_refinement_loop",
    max_iterations=50,  # Default safeguard, overridden by LoopConfigAgent
    sub_agents=[
        unified_researcher,     # Performs initial OR refinement research
        research_evaluator,     # Always evaluates the work done
        EscalationChecker(name="escalation_checker"), # Checks if we're all done
    ],
)

# Define the final, improved research pipeline.
research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="Executes the approved research plan by initializing a brief, iteratively gathering facts, and then composing a final JSON brief.",
    sub_agents=[
        section_planner,
        LoopConfigAgent(loop_agent=iterative_refinement_loop),
        iterative_refinement_loop,
        brief_finalizer,
    ],
)