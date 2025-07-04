import logging
import re
import json

from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types
from pydantic import ValidationError

# Import our project's specific schemas
from ..schemas.narrative import NarrativePlan
from ..schemas.brief import ResearchStatus, NodeUpdate

def save_plan_to_state_callback(callback_context: CallbackContext) -> None:
    """
    Finds the JSON string from the plan_generator's output, parses it into a
    NarrativePlan object, and saves it and the original subject to the session state.
    
    This callback is now resilient to conversational text before the JSON.
    """
    session = callback_context._invocation_context.session
    plan_saved = False
    
    # First, find the original user query from the first human event
    for event in session.events:
        if event.author == "user" and event.content and event.content.parts:
            user_query = event.content.parts[0].text
            callback_context.state["research_subject"] = user_query
            logging.info(f"Successfully saved 'research_subject': '{user_query}' to state.")
            break

    for event in reversed(session.events):
        if plan_saved:
            break

        if not event.content or not event.content.parts:
            continue

        for part in event.content.parts:
            if not part.function_response or part.function_response.name != "plan_generator":
                continue

            response_data = part.function_response.response
            if not isinstance(response_data, dict) or "result" not in response_data:
                continue
            
            full_output_string = response_data["result"]

            if isinstance(full_output_string, str):
                # --- THE CRITICAL FIX IS HERE ---
                # Use a regular expression to find the JSON block.
                # This looks for a string that starts with '{' and ends with '}'.
                # The re.DOTALL flag allows '.' to match newlines.
                json_match = re.search(r'\{.*\}', full_output_string, re.DOTALL)
                
                if not json_match:
                    logging.error(f"Could not find a JSON block in the output from 'plan_generator'.")
                    continue

                json_string = json_match.group(0)
                # --- END OF FIX ---

                try:
                    plan_object = NarrativePlan.model_validate_json(json_string)
                    callback_context.state["research_plan"] = plan_object
                    logging.info(f"Successfully parsed and saved '{type(plan_object).__name__}' to state.")
                    plan_saved = True
                    break

                except (ValidationError, json.JSONDecodeError) as e:
                    logging.error(f"Failed to parse JSON from plan_generator: {e}")
                    return

    if not plan_saved:
        logging.warning(
            "Callback ran, but could not find a valid JSON response from 'plan_generator' to save."
        )

def update_brief_with_research_callback(callback_context: CallbackContext) -> None:
    """
    Finds a JSON string in a research agent's output, parses it into a
    NodeUpdate object, and merges the data into the main documentary_brief.
    """
    session = callback_context._invocation_context.session
    if not (brief := callback_context.state.get("documentary_brief")):
        logging.warning("Callback ran, but 'documentary_brief' not found in state.")
        return

    # Find the most recent text output from our research agents
    for event in reversed(session.events):
        if (event.author in ("section_researcher", "enhanced_search_executor", "unified_researcher") and
            event.content and event.content.parts):
            
            # The output is in the text part of the final agent response
            json_string = event.content.parts[0].text
            
            # Ensure the string is not None or empty before trying to parse it.
            if json_string:
                try:
                    node_update = NodeUpdate.model_validate_json(json_string)

                    # Find the matching node in the brief and update it
                    for node in brief.knowledge_nodes:
                        if node.node_title == node_update.node_title:
                            # Merge sources and facts
                            existing_urls = {s.url for s in node.top_sources}
                            for new_source in node_update.top_sources:
                                if new_source.url not in existing_urls:
                                    node.top_sources.append(new_source)

                            existing_facts = {f.description for f in node.fact_points}
                            for new_fact in node_update.fact_points:
                                if new_fact.description not in existing_facts:
                                    node.fact_points.append(new_fact)

                            node.research_status = ResearchStatus.ACTIVE
                            
                            logging.info(f"Successfully updated node '{node.node_title}' with {len(node_update.fact_points)} new facts.")
                            callback_context.state["documentary_brief"] = brief
                            return # Exit after successful update

                except (ValidationError, json.JSONDecodeError, IndexError) as e:
                    logging.debug(f"Skipping event output, not a valid JSON NodeUpdate: {e}")
                    continue

    logging.warning("Callback ran but could not find a valid 'NodeUpdate' JSON to process.")


def collect_research_sources_callback(callback_context: CallbackContext) -> None:
    """Collects and organizes web-based research sources and their supported claims from agent events.

    This function processes the agent's `session.events` to extract web source details (URLs,
    titles, domains from `grounding_chunks`) and associated text segments with confidence scores
    (from `grounding_supports`). The aggregated source information and a mapping of URLs to short
    IDs are cumulatively stored in `callback_context.state`.

    Args:
        callback_context (CallbackContext): The context object providing access to the agent's
            session events and persistent state.
    """
    session = callback_context._invocation_context.session
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1
    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue
        chunks_info = {}
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            if not chunk.web:
                continue
            url = chunk.web.uri
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )
            if url not in url_to_short_id:
                short_id = f"src-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "supported_claims": [],
                }
                id_counter += 1
            chunks_info[idx] = url_to_short_id[url]
        if event.grounding_metadata.grounding_supports:
            for support in event.grounding_metadata.grounding_supports:
                confidence_scores = support.confidence_scores or []
                chunk_indices = support.grounding_chunk_indices or []
                for i, chunk_idx in enumerate(chunk_indices):
                    if chunk_idx in chunks_info:
                        short_id = chunks_info[chunk_idx]
                        confidence = (
                            confidence_scores[i] if i < len(confidence_scores) else 0.5
                        )
                        text_segment = support.segment.text if support.segment else ""
                        sources[short_id]["supported_claims"].append(
                            {
                                "text_segment": text_segment,
                                "confidence": confidence,
                            }
                        )
    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources


def citation_replacement_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """Replaces citation tags in a report with Markdown-formatted links.

    Processes 'final_cited_report' from context state, converting tags like
    `<cite source="src-N"/>` into hyperlinks using source information from
    `callback_context.state["sources"]`. Also fixes spacing around punctuation.

    Args:
        callback_context (CallbackContext): Contains the report and source information.

    Returns:
        genai_types.Content: The processed report with Markdown citation links.
    """
    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            logging.warning(f"Invalid citation tag found and removed: {match.group(0)}")
            return ""
        display_text = source_info.get("title", source_info.get("domain", short_id))
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    callback_context.state["final_report_with_citations"] = processed_report
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])

# This callback's return value will REPLACE the agent's output to the user.
def display_confirmation_callback(callback_context: CallbackContext) -> genai_types.Content:
    """
    Replaces the complex DocumentaryBrief object with a simple confirmation
    message for the user.
    """
    logging.info("Brief created in state. Displaying confirmation to user.")
    confirmation_text = (
        "Plan approved. I have now structured the research brief "
        "and am proceeding to the autonomous research phase."
    )
    return genai_types.Content(parts=[genai_types.Part(text=confirmation_text)])