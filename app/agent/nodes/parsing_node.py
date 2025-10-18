"""Parsing node - uses LLM to extract filters from the prompt."""

import json
from typing import Dict, Any, List, Union
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import get_settings
from app.core.logger import get_logger
from app.agent.utils import get_all_supported_fields

logger = get_logger(__name__)


def parsing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse the prompt using LLM to extract structured filters.
    
    Args:
        state: Current agent state containing 'prompt' and 'language'
        
    Returns:
        Updated state with 'raw_filters'
    """
    prompt = state.get("prompt", "")
    language = state.get("language", "en")
    
    logger.info("Parsing node processing", language=language)
    
    try:
        # Initialize LLM
        settings = get_settings()
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            openai_api_key=settings.openai_api_key,
        )
        
        # Create JSON output parser
        parser = JsonOutputParser()
        
        # Get supported fields
        supported_fields = get_all_supported_fields()
        
        # Create prompt template
        template = """You are an expert at parsing natural language prompts into structured audience filters.

Your task is to extract filters from the user's prompt and convert them into a structured JSON format.

Supported Fields:
{supported_fields}

Supported Operators:
- = (equals)
- != (not equals)
- < (less than)
- > (greater than)
- <= (less than or equal)
- >= (greater than or equal)
- between (for ranges, value should be a list of two elements)

Guidelines:
1. Extract ALL filters mentioned in the prompt
2. Use exact field names from the supported fields list
3. Convert dates to YYYY-MM-DD format when possible
4. For "between" operator, use a list with two values: [min, max]
5. Preserve numeric values as numbers (not strings)
6. For gender, use "Male" or "Female"
7. If the prompt is in Arabic, translate field values to English where appropriate

User Prompt ({language}):
{prompt}

You MUST respond with valid JSON in this exact format:
{{
  "filters": [
    {{
      "field": "field_name",
      "operator": "operator",
      "value": "value or [min, max] for between"
    }}
  ]
}}

If no filters can be extracted, return: {{"filters": []}}

Do not include any explanation, only return the JSON object.
"""
        
        prompt_template = ChatPromptTemplate.from_template(template)
        
        # Create the chain
        chain = prompt_template | llm | parser
        
        # Execute the chain
        result = chain.invoke({
            "prompt": prompt,
            "language": language,
            "supported_fields": ", ".join(supported_fields),
        })
        
        # Extract filters from result
        raw_filters = result.get("filters", [])
        
        logger.info("Parsing completed", filter_count=len(raw_filters))
        
        return {
            **state,
            "raw_filters": raw_filters,
        }
        
    except Exception as e:
        logger.error("Parsing failed", error=str(e), prompt=prompt)
        return {
            **state,
            "raw_filters": [],
            "errors": state.get("errors", []) + [f"Parsing error: {str(e)}"],
        }

