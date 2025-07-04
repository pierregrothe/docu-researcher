from pydantic import BaseModel, Field
from typing import Literal, List
from enum import Enum
import datetime

class ResearchStatus(str, Enum):
    """Defines the research status for a knowledge node."""
    PENDING = "pending"
    ACTIVE = "active"
    SATURATED = "saturated"
    STALLED = "stalled"

class TopSource(BaseModel):
    """A single, high-quality source identified for a knowledge node."""
    url: str
    title: str
    rationale: str = Field(description="A brief explanation of why this source is valuable.")

class FactPoint(BaseModel):
    """A single, structured, and narratively-contextualized fact."""
    fact_id: str
    description: str = Field(description="The core fact, stated clearly and concisely.")
    
    category: Literal[
        "Key Event", "Key Figure", "Quirky Anecdote", 
        "Technical Detail", "World-Building"
    ] = Field(description="The classification of the fact to help with story structure.")
    
    narrative_significance: int = Field(
        description="Story Impact (1-10): How crucial is this for the main narrative?"
    )
    
    visual_suggestion: str = Field(
        description="A suggestion for how to visually represent this fact (e.g., 'Archival footage of the launch,' 'Animated map')."
    )
    
    related_entities: list[str] = Field(
        description="A list of key people, places, or concepts this fact is directly related to."
    )

    related_fact_ids: list[str] = Field(
        description="A list of unique fact_ids that this fact is narratively connected to.",
        default_factory=list
    )
    
    source_url: str

class KnowledgeNode(BaseModel):
    """A single, trackable unit of research containing its rationale, top sources, and extracted facts."""
    node_title: str
    rationale: str
    # Add the axis discriminator here as well
    axis: Literal["chronological", "thematic", "key_figures_and_entities"] = Field(
        description="The narrative axis this node belongs to."
    )
    research_status: ResearchStatus = Field(default=ResearchStatus.PENDING)
    top_sources: list[TopSource] = Field(default_factory=list)
    fact_points: list[FactPoint] = Field(default_factory=list)

class DocumentaryBrief(BaseModel):
    """The final, comprehensive JSON data file that tracks the entire research process."""
    reference_id: str = Field(description="The unique reference ID for this research task.")
    subject: str = Field(description="The original high-level subject provided by the user.")
    generation_date: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    narrative_summary: str
    # This is now a simple, flat list of knowledge nodes.
    knowledge_nodes: list[KnowledgeNode]

class NodeUpdate(BaseModel):
    """A model to hold the research results for a single KnowledgeNode."""
    node_title: str = Field(description="The title of the node being updated, used for identification.")
    top_sources: list[TopSource] = Field(description="A list of the top sources found for this node.")
    fact_points: list[FactPoint] = Field(description="A list of structured facts extracted from the sources.")

class SearchQuery(BaseModel):
    """Model representing a specific search query for web search."""

    search_query: str = Field(
        description="A highly specific and targeted query for web search."
    )

class Feedback(BaseModel):
    """Model for providing evaluation feedback on research quality."""

    grade: Literal["pass", "fail"] = Field(
        description="Evaluation result. 'pass' if the research is sufficient, 'fail' if it needs revision."
    )
    comment: str = Field(
        description="Detailed explanation of the evaluation, highlighting strengths and/or weaknesses of the research."
    )
    follow_up_queries: list[SearchQuery] | None = Field(
        default=None,
        description="A list of specific, targeted follow-up search queries needed to fix research gaps. This should be null or empty if the grade is 'pass'.",
    )