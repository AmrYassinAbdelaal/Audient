"""LangGraph workflow builder for the audience filter agent."""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.core.logger import get_logger
from app.agent.nodes import input_node, parsing_node, validation_node, output_node

logger = get_logger(__name__)


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph workflow.
    
    The workflow consists of four nodes:
    1. Input Node - receives and prepares the prompt
    2. Parsing Node - uses LLM to extract filters
    3. Validation Node - validates and normalizes filters
    4. Output Node - formats the final response
    
    Returns:
        Compiled StateGraph workflow
    """
    logger.info("Building agent graph")
    
    # Create the graph
    workflow = StateGraph(Dict[str, Any])
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("parsing", parsing_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("output", output_node)
    
    # Define the flow
    workflow.set_entry_point("input")
    workflow.add_edge("input", "parsing")
    workflow.add_edge("parsing", "validation")
    workflow.add_edge("validation", "output")
    workflow.add_edge("output", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("Agent graph built successfully")
    
    return app

