"""Custom exceptions and error handling for the AI Audience Agent."""

from typing import List, Optional, Dict, Any


class AudienceAgentError(Exception):
    """Base exception for all AI Audience Agent errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class UnsupportedFieldError(AudienceAgentError):
    """Raised when an unsupported field is detected."""
    
    def __init__(self, field: str, supported_fields: List[str]):
        message = (
            f"The field '{field}' is not supported. "
            f"Please use one of: {', '.join(supported_fields)}"
        )
        super().__init__(message, {"field": field, "supported_fields": supported_fields})


class UnsupportedOperatorError(AudienceAgentError):
    """Raised when an unsupported operator is detected."""
    
    def __init__(self, operator: str, field: str, valid_operators: List[str]):
        message = (
            f"The operator '{operator}' is not supported for field '{field}'. "
            f"Valid operators are: {', '.join(valid_operators)}"
        )
        super().__init__(
            message,
            {"operator": operator, "field": field, "valid_operators": valid_operators}
        )


class MissingValueError(AudienceAgentError):
    """Raised when a required value is missing."""
    
    def __init__(self, field: str, example: Optional[str] = None):
        example_text = f" (e.g., {example})" if example else ""
        message = f"Please provide a value for '{field}'{example_text}."
        super().__init__(message, {"field": field})


class AmbiguousDateError(AudienceAgentError):
    """Raised when a date reference is ambiguous."""
    
    def __init__(self, original_text: str, suggestions: List[str]):
        message = (
            f"The date reference '{original_text}' is ambiguous. "
            f"Did you mean: {' or '.join(suggestions)}?"
        )
        super().__init__(
            message,
            {"original_text": original_text, "suggestions": suggestions}
        )


class InvalidValueTypeError(AudienceAgentError):
    """Raised when a value type doesn't match the expected type."""
    
    def __init__(self, field: str, value: Any, expected_type: str):
        message = (
            f"Invalid value type for field '{field}'. "
            f"Expected {expected_type}, got: {value}"
        )
        super().__init__(
            message,
            {"field": field, "value": value, "expected_type": expected_type}
        )


class ParsingError(AudienceAgentError):
    """Raised when prompt parsing fails."""
    
    def __init__(self, prompt: str, reason: Optional[str] = None):
        message = f"Failed to parse prompt: {prompt}"
        if reason:
            message += f". Reason: {reason}"
        super().__init__(message, {"prompt": prompt, "reason": reason})


class ValidationError(AudienceAgentError):
    """Raised when filter validation fails."""
    
    def __init__(self, filters: List[Dict[str, Any]], errors: List[str]):
        message = f"Filter validation failed: {'; '.join(errors)}"
        super().__init__(message, {"filters": filters, "errors": errors})

