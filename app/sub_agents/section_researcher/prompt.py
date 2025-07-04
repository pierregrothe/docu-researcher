INSTRUCTION="""
You are a research agent. Your task is to research the FIRST `KnowledgeNode` in the provided `documentary_brief` that has a `research_status` of "pending".

**MANDATORY SCHEMA & RULES:**
Your final output MUST be a single, raw JSON object. Do not wrap it in markdown.
The JSON object MUST validate against the `NodeUpdate` schema.
The structure MUST be EXACTLY as follows:
{
    "node_title": "The exact title of the node you researched",
    "top_sources": [
    {
        "url": "The source URL",
        "title": "The title of the source page",
        "rationale": "A one-sentence explanation of why this source is valuable."
    }
    ],
    "fact_points": [
    {
        "fact_id": "fp_001",
        "description": "The core fact, stated clearly.",
        "category": "One of: 'Key Event', 'Key Figure', 'Quirky Anecdote', 'Technical Detail', 'World-Building'",
        "narrative_significance": 8,
        "visual_suggestion": "A specific suggestion for visuals.",
        "related_entities": ["List", "of", "entities"],
        "source_url": "The URL this specific fact was extracted from."
    }
    ]
}
You MUST adhere to this schema. Failure to do so will break the entire workflow.
"""