"""Input node - receives and prepares the user prompt."""

from typing import Dict, Any
from app.core.logger import get_logger

logger = get_logger(__name__)


def input_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Process the input prompt and prepare it for parsing.
    
    Args:
        state: Current agent state containing 'prompt'
        
    Returns:
        Updated state with processed prompt
    """
    prompt = state.get("prompt", "").strip()
    
    logger.info("Input node processing", prompt=prompt[:100])
    
    # Detect language (simple heuristic)
    has_arabic = any('\u0600' <= char <= '\u06FF' for char in prompt)
    language = "ar" if has_arabic else "en"
    
    return {
        **state,
        "prompt": prompt,
        "language": language,
        "errors": [],
    }

