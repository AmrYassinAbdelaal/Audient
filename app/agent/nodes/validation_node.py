"""Validation node - validates and normalizes extracted filters."""

from typing import Dict, Any, List
from app.core.logger import get_logger
from app.agent.utils import (
    load_supported_fields,
    normalize_field_name,
    normalize_operator,
    normalize_value,
    validate_filter,
)

logger = get_logger(__name__)


def validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the extracted filters.
    
    Args:
        state: Current agent state containing 'raw_filters'
        
    Returns:
        Updated state with 'validated_filters' and any validation errors
    """
    raw_filters = state.get("raw_filters", [])
    errors = state.get("errors", [])
    
    logger.info("Validation node processing", filter_count=len(raw_filters))
    
    # Load configuration
    config = load_supported_fields()
    
    validated_filters = []
    validation_errors = []
    
    for i, filter_dict in enumerate(raw_filters):
        try:
            # Normalize field name
            field = filter_dict.get("field", "")
            normalized_field = normalize_field_name(field)
            
            # Normalize operator
            operator = filter_dict.get("operator", "")
            normalized_operator = normalize_operator(operator)
            
            # Get field type
            field_type = config["field_types"].get(normalized_field, "string")
            
            # Normalize value
            value = filter_dict.get("value")
            if isinstance(value, list):
                # For 'between' operator or list values
                normalized_value = [
                    normalize_value(normalized_field, v, field_type) for v in value
                ]
            else:
                normalized_value = normalize_value(normalized_field, value, field_type)
            
            # Create normalized filter
            normalized_filter = {
                "field": normalized_field,
                "operator": normalized_operator,
                "value": normalized_value,
            }
            
            # Validate the filter
            filter_errors = validate_filter(normalized_filter, config)
            
            if filter_errors:
                validation_errors.extend(
                    [f"Filter {i+1}: {error}" for error in filter_errors]
                )
                logger.warning(
                    "Filter validation failed",
                    filter_index=i,
                    filter=normalized_filter,
                    errors=filter_errors,
                )
            else:
                validated_filters.append(normalized_filter)
                logger.debug(
                    "Filter validated successfully",
                    filter_index=i,
                    filter=normalized_filter,
                )
        
        except Exception as e:
            error_msg = f"Filter {i+1}: Validation exception - {str(e)}"
            validation_errors.append(error_msg)
            logger.error(
                "Filter validation exception",
                filter_index=i,
                filter=filter_dict,
                error=str(e),
            )
    
    # Combine all errors
    all_errors = errors + validation_errors
    
    logger.info(
        "Validation completed",
        validated_count=len(validated_filters),
        error_count=len(validation_errors),
    )
    
    return {
        **state,
        "validated_filters": validated_filters,
        "errors": all_errors,
    }

