"""Output node - formats the final response."""

from typing import Dict, Any
from app.core.logger import get_logger

logger = get_logger(__name__)


def output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Format the final output with validated filters.
    
    Args:
        state: Current agent state containing 'validated_filters' and 'errors'
        
    Returns:
        Updated state with 'output' containing the final result
    """
    validated_filters = state.get("validated_filters", [])
    errors = state.get("errors", [])
    
    logger.info(
        "Output node processing",
        filter_count=len(validated_filters),
        error_count=len(errors),
    )
    
    # Create the output
    output = {
        "filters": validated_filters,
    }
    
    # Include errors if any (for debugging, but API will handle error responses separately)
    if errors:
        output["errors"] = errors
    
    return {
        **state,
        "output": output,
    }

