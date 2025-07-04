```
  ____                 _           _
 |  _ \ _ __ ___  _   _| |__   ___ | |_ ___  ___
 | |_) | '__/ _ \| | | | '_ \ / _ \| __/ _ \ __|
 |  __/| | | (_) | |_| | |_) | (_) | ||  __/\__ \
 |_|   |_|  \___/ \__, |_.__/ \___/ \__\___||___/
                  |___/
```
# AI Documentary Research Assistant

This project is a sophisticated, full-stack multi-agent system designed to automate the pre-production research phase for creative professionals like documentary producers, scriptwriters, and YouTube creators. It transforms a high-level topic into a comprehensive, story-driven, and fact-checked JSON research brief.

The system uses the Google Agent Development Kit (ADK) to orchestrate a team of specialized AI agents that collaborate to plan a narrative, discover sources, extract structured facts, and build a rich, interconnected knowledge base.

### Key Features

* **🧠 Intelligent Planning:** An `InteractivePlanner` agent collaborates with the user to create a multi-axis research plan, ensuring the final output aligns with the user's creative vision.
* **🔄 Autonomous Research Loop:** A robust `LoopAgent` iterates through each narrative point, performing deep research, extracting facts, and self-critiquing its own work to identify and fill knowledge gaps.
* **📊 Structured Data Output:** Instead of a prose report, the final deliverable is a single, comprehensive JSON file containing structured, categorized, and narratively-contextualized facts.
* **🕸️ Knowledge Graph Construction:** The final agent, `BriefFinalizer`, analyzes the complete dataset to create relational links between facts, building a web of interconnected knowledge that is invaluable for story development.
* **⚛️ Modular & Adaptable:** Built with the ADK, each agent has a specific purpose, making the system easy to understand, maintain, and extend.

## The Final Output: A DocumentaryBrief JSON

The end product of the agent's workflow is not a text document, but a single, detailed JSON file. This file acts as a complete "briefing book" for a creative team.

The structure is defined by the `DocumentaryBrief` schema:

```python
class DocumentaryBrief(BaseModel):
    reference_id: str
    subject: str
    generation_date: str
    narrative_summary: str
    knowledge_nodes: list[KnowledgeNode]

class KnowledgeNode(BaseModel):
    node_title: str
    rationale: str
    research_status: ResearchStatus # e.g., "pending", "active", "saturated"
    top_sources: list[TopSource]
    fact_points: list[FactPoint]

class FactPoint(BaseModel):
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
```

## How the Agent Thinks: The Architectural Workflow

The system operates in two distinct phases, using a series of specialized agents defined in `app/agent.py`.

<!-- It's recommended to replace this with a real diagram link -->

### Phase 1: Plan & Refine (Human-in-the-Loop)

This initial phase is identical to the original `gemini-fullstack` example, ensuring user control over the creative direction.

1.  **`interactive_planner_agent`**: Takes the user's topic.
2.  **`plan_generator` (Tool)**: Creates a multi-axis `NarrativePlan` (chronological, thematic, key figures).
3.  **User Approval**: The plan is presented to the user. The workflow does not proceed without explicit approval (e.g., the user typing "proceed").

### Phase 2: Autonomous Fact-Finding & Assembly

Once the plan is approved, the `research_pipeline` takes over and operates autonomously.

1.  **`section_planner` (Adapted Role: Brief Initializer)**: This agent's first task is to take the approved plan and create the skeleton of the `DocumentaryBrief` JSON object. It populates the top-level information and creates the list of `KnowledgeNode`s, setting each one's `research_status` to "pending".

2.  **`iterative_refinement_loop` (The Research Engine)**: This loop runs until every `KnowledgeNode` is marked as "saturated".
    * **`section_researcher`**: Selects the next "pending" node. It executes its search queries, finds sources, and extracts `FactPoint` objects that match our detailed schema. It then updates the `documentary_brief` in the agent's state via the `update_brief_with_research_callback`.
    * **`research_evaluator` (Adapted Role: AI Story Editor)**: This critic agent examines the newly added facts for the now "active" node. It assesses relevance, narrative significance, and balance. It uses the "Diminishing Returns" model to determine if the node is saturated. If research is sufficient, it grades "pass". If gaps remain, it grades "fail" and provides specific follow-up queries.
    * **`EscalationChecker` (Adapted Role: Intelligent Loop Controller)**: This agent checks the evaluator's grade.
        * If "pass", it marks the current node as "saturated" and the loop continues to the next pending node.
        * If "fail", it leaves the node as "active", allowing the next agent in the loop to run.
        * Only when **all** nodes are "saturated" does it escalate to stop the entire loop.
    * **`enhanced_search_executor`**: If the evaluation grade was "fail", this agent runs, using the targeted follow-up queries to find the missing facts and enrich the brief. The loop then repeats with the `research_evaluator`.

3.  **`BriefFinalizer` (Formerly `report_composer`)**: Once the loop is complete, this agent performs two final tasks:
    * **Knowledge Graph Construction**: It analyzes the complete set of facts and populates the `related_fact_ids` for each one, creating connections between them.
    * **Final Output**: It presents the final, complete, and interconnected `DocumentaryBrief` JSON as the definitive output of the workflow.


## Getting Started

**Prerequisites:** **[Python 3.10+](https://www.python.org/downloads/)**, **[Node.js](https://nodejs.org/)**, and **[uv](https://github.com/astral-sh/uv)**.

### A. Using a Google AI Studio API Key

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/gemini-fullstack 
    ```
2.  **Set Environment Variables:** Create a `.env` file in the `app` folder (replace `YOUR_AI_STUDIO_API_KEY`):
    ```bash
    echo "GOOGLE_GENAI_USE_VERTEXAI=FALSE" >> app/.env
    echo "GOOGLE_API_KEY=YOUR_AI_STUDIO_API_KEY" >> app/.env
    ```
3.  **Install & Run:**
    ```bash
    make install && make dev
    ```


### B. Using Google Cloud Vertex AI


1.  **Create Project from Template:**
    ```bash
    uvx agent-starter-pack create my-docu-researcher -a adk_gemini_fullstack
    ```
2.  **Install & Run:**
    ```bash
    cd my-docu-researcher
    make install && make dev
    ```

Your AI Documentary Research Assistant is now running at **`http://localhost:5173`**.