"""Utility functions for the agent."""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Union
from datetime import datetime, timedelta
from dateutil import parser as date_parser

from app.core.logger import get_logger

logger = get_logger(__name__)


def load_supported_fields() -> Dict[str, Any]:
    """Load supported fields configuration from JSON file."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    fields_file = data_dir / "supported_fields.json"
    
    with open(fields_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_value_mappings() -> Dict[str, Any]:
    """Load value mappings for normalization from JSON file."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    mappings_file = data_dir / "value_mappings.json"
    
    with open(mappings_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_supported_fields() -> List[str]:
    """Get a flat list of all supported field names."""
    config = load_supported_fields()
    all_fields = []
    for category in config["fields"].values():
        all_fields.extend(category)
    return all_fields


def normalize_field_name(field: str) -> str:
    """Normalize field name to match supported fields.
    
    Args:
        field: The field name to normalize
        
    Returns:
        Normalized field name or original if no match found
    """
    field = field.lower().strip().replace(" ", "_")
    
    # Common field name variations
    field_aliases = {
        "sex": "gender",
        "join_date": "joining_date",
        "signup_date": "joining_date",
        "registration_date": "joining_date",
        "orders": "total_orders",
        "order_count": "total_orders",
        "num_orders": "total_orders",
        "sales": "total_sales",
        "revenue": "total_sales",
        "rating": "store_rating",
        "last_order": "latest_purchase",
        "last_purchase": "latest_purchase",
    }
    
    return field_aliases.get(field, field)


def normalize_operator(operator: str) -> str:
    """Normalize operator to standard format.
    
    Args:
        operator: The operator to normalize
        
    Returns:
        Normalized operator
    """
    operator = operator.strip()
    
    operator_aliases = {
        "equals": "=",
        "equal": "=",
        "is": "=",
        "not equals": "!=",
        "not equal": "!=",
        "is not": "!=",
        "greater than": ">",
        "more than": ">",
        "gt": ">",
        "less than": "<",
        "lt": "<",
        "greater than or equal": ">=",
        "at least": ">=",
        "gte": ">=",
        "less than or equal": "<=",
        "at most": "<=",
        "lte": "<=",
        "in range": "between",
        "range": "between",
    }
    
    return operator_aliases.get(operator.lower(), operator)


def normalize_value(field: str, value: Any, field_type: str) -> Any:
    """Normalize a value based on field type and mappings.
    
    Args:
        field: The field name
        value: The value to normalize
        field_type: The expected field type
        
    Returns:
        Normalized value
    """
    mappings = load_value_mappings()
    
    # Handle string values
    if isinstance(value, str):
        value = value.strip()
        
        # Apply field-specific mappings
        if field == "gender" and value.lower() in mappings["gender_mappings"]:
            return mappings["gender_mappings"][value.lower()]
        
        if field == "country":
            for key, mapped_value in mappings["country_mappings"].items():
                if key.lower() in value.lower():
                    return mapped_value
        
        if field == "city":
            for key, mapped_value in mappings["city_mappings"].items():
                if key.lower() in value.lower() or value.lower() in key.lower():
                    return mapped_value
        
        # Boolean mappings
        if field_type == "boolean" and value.lower() in mappings["boolean_mappings"]:
            return mappings["boolean_mappings"][value.lower()]
        
        # Date parsing
        if field_type == "date":
            return parse_date(value)
    
    # Handle numeric values
    if field_type == "integer" and not isinstance(value, bool):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            pass
    
    if field_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError):
            pass
    
    return value


def parse_date(date_str: str) -> str:
    """Parse a date string into YYYY-MM-DD format.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Date in YYYY-MM-DD format
    """
    date_str = date_str.strip()
    mappings = load_value_mappings()
    
    # Handle relative dates
    if "last" in date_str.lower():
        days_match = re.search(r"(\d+)\s*days?", date_str, re.IGNORECASE)
        if days_match:
            days = int(days_match.group(1))
            target_date = datetime.now() - timedelta(days=days)
            return target_date.strftime("%Y-%m-%d")
    
    # Replace month names with numbers
    for month_name, month_num in mappings["month_names"].items():
        pattern = re.compile(re.escape(month_name), re.IGNORECASE)
        date_str = pattern.sub(month_num, date_str)
    
    # Try to parse the date
    try:
        parsed_date = date_parser.parse(date_str, fuzzy=True)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning("Failed to parse date", date_str=date_str, error=str(e))
        return date_str


def validate_filter(filter_dict: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """Validate a single filter against the configuration.
    
    Args:
        filter_dict: The filter to validate
        config: The supported fields configuration
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    field = filter_dict.get("field")
    operator = filter_dict.get("operator")
    value = filter_dict.get("value")
    
    # Validate field
    all_fields = []
    for category in config["fields"].values():
        all_fields.extend(category)
    
    if field not in all_fields:
        errors.append(f"Unsupported field: {field}")
        return errors  # Return early if field is invalid
    
    # Validate operator
    if operator not in config["operators"]:
        errors.append(f"Unsupported operator: {operator}")
    
    # Validate operator is valid for field type
    field_type = config["field_types"].get(field)
    if field_type:
        valid_ops = config["valid_operators_per_type"].get(field_type, [])
        if operator not in valid_ops:
            errors.append(
                f"Operator '{operator}' is not valid for field '{field}' of type '{field_type}'"
            )
    
    # Validate value
    if value is None or (isinstance(value, str) and not value.strip()):
        errors.append(f"Missing value for field: {field}")
    
    # Validate 'between' operator has list value
    if operator == "between":
        if not isinstance(value, list) or len(value) != 2:
            errors.append(
                f"Operator 'between' requires a list of two values for field: {field}"
            )
    
    return errors

