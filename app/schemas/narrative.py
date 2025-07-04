from pydantic import BaseModel, Field

# app/schemas/narrative.py

from pydantic import BaseModel, Field

from pydantic import BaseModel, Field
from typing import Literal

# This schema is now simpler and includes the new 'axis' field.
class KnowledgeNodePlan(BaseModel):
    """Represents a plan for a single knowledge node, including its axis and queries."""
    node_title: str = Field(description="A concise, descriptive title for the node.")
    rationale: str = Field(description="A single sentence explaining the node's narrative importance.")
    # Add the axis discriminator
    axis: Literal["chronological", "thematic", "key_figures_and_entities"] = Field(
        description="The narrative axis this node belongs to."
    )
    search_queries: list[str] = Field(description="A comprehensive list of expert-level search queries.")

# The NarrativePlan now contains a single, flat list of nodes.
class NarrativePlan(BaseModel):
    """The final, comprehensive research plan, structured as a single list of nodes."""
    narrative_summary: str = Field(description="A brief, high-level overview of the documentary's story.")
    # This is now a simple list, not a complex object.
    knowledge_nodes: list[KnowledgeNodePlan]