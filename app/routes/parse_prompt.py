"""Parse prompt endpoint - converts natural language to structured filters."""

from fastapi import APIRouter, HTTPException, status
from app.schemas import PromptRequest, FilterResponse, ErrorResponse
from app.agent import build_agent_graph
from app.agent.observability import get_observability_manager
from app.core.logger import get_logger
from app.core.errors import AudienceAgentError

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["parse"])

# Initialize the agent graph once
agent_graph = None


def get_agent_graph():
    """Lazy initialization of the agent graph."""
    global agent_graph
    if agent_graph is None:
        agent_graph = build_agent_graph()
    return agent_graph


@router.post(
    "/parse_prompt",
    response_model=FilterResponse,
    responses={
        200: {
            "description": "Successfully parsed prompt into filters",
            "model": FilterResponse,
        },
        400: {
            "description": "Invalid request or parsing error",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
    summary="Parse Natural Language Prompt",
    description="Converts a natural language prompt (English or Arabic) into structured audience filters",
)
async def parse_prompt(request: PromptRequest) -> FilterResponse:
    """Parse a natural language prompt into structured filters.
    
    Args:
        request: The prompt request containing the natural language text
        
    Returns:
        FilterResponse with the parsed filters
        
    Raises:
        HTTPException: If parsing or validation fails
    """
    observability = get_observability_manager()
    
    try:
        # Log the incoming prompt
        logger.info("Received parse request", prompt=request.prompt[:100])
        
        # Get the agent graph
        graph = get_agent_graph()
        
        # Execute the graph with tracing
        with observability.trace_run("parse_prompt", {"prompt_length": len(request.prompt)}):
            # Log prompt
            observability.log_prompt(request.prompt, "unknown")
            
            # Run the agent
            initial_state = {
                "prompt": request.prompt,
            }
            
            result = graph.invoke(initial_state)
            
            # Extract output
            output = result.get("output", {})
            filters = output.get("filters", [])
            errors = output.get("errors", [])
            
            # Log results
            observability.log_final_output(output)
            
            # Check for errors
            if errors:
                logger.warning("Parsing completed with errors", errors=errors, filter_count=len(filters))
                
                # If no filters were extracted, return error
                if not filters:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Failed to parse prompt into valid filters",
                            "details": {"errors": errors}
                        }
                    )
            
            logger.info("Parse request successful", filter_count=len(filters))
            
            return FilterResponse(filters=filters)
    
    except AudienceAgentError as e:
        logger.error("Audience agent error", error=str(e), details=e.details)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.message,
                "details": e.details
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error("Unexpected error during parsing", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error during prompt parsing",
                "details": {"message": str(e)}
            }
        )

