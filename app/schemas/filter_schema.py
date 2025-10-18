"""Response schemas for filter outputs."""

from typing import Any, List, Union, Optional, Dict
from pydantic import BaseModel, Field, field_validator


class Filter(BaseModel):
    """A single audience filter.
    
    Attributes:
        field: The field name (e.g., 'gender', 'total_orders')
        operator: The comparison operator (e.g., '=', '>', 'between')
        value: The filter value (can be string, number, date, list, or boolean)
    """
    
    field: str = Field(
        ...,
        description="The field name to filter on",
        examples=["gender", "total_orders", "joining_date"]
    )
    
    operator: str = Field(
        ...,
        description="The comparison operator",
        examples=["=", ">", "between", "!="]
    )
    
    value: Union[str, int, float, bool, List[Union[str, int, float]]] = Field(
        ...,
        description="The value(s) to filter by",
        examples=["Female", 5, [3, 5], "2023-01-01"]
    )
    
    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        """Validate that operator is one of the supported operators."""
        valid_operators = ["=", "!=", "<", ">", "<=", ">=", "between"]
        if v not in valid_operators:
            raise ValueError(f"Operator must be one of: {', '.join(valid_operators)}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "field": "gender",
                    "operator": "=",
                    "value": "Female"
                },
                {
                    "field": "total_orders",
                    "operator": ">",
                    "value": 5
                },
                {
                    "field": "store_rating",
                    "operator": "between",
                    "value": [3, 5]
                }
            ]
        }
    }


class FilterResponse(BaseModel):
    """Response model containing parsed filters.
    
    Attributes:
        filters: List of parsed filter objects
    """
    
    filters: List[Filter] = Field(
        ...,
        description="List of parsed audience filters",
        min_length=0
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filters": [
                        {"field": "gender", "operator": "=", "value": "Female"},
                        {"field": "total_orders", "operator": ">", "value": 10}
                    ]
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model.
    
    Attributes:
        error: Error message
        details: Additional error details
    """
    
    error: str = Field(
        ...,
        description="Error message"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "The field 'email_open_rate' is not supported",
                    "details": {
                        "field": "email_open_rate",
                        "supported_fields": ["gender", "total_orders", "..."]
                    }
                }
            ]
        }
    }

