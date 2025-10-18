"""Request schema for prompt parsing endpoint."""

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    """Request model for parsing a user prompt into filters.
    
    Attributes:
        prompt: The natural language prompt in English or Arabic
    """
    
    prompt: str = Field(
        ...,
        description="Natural language prompt describing audience filters",
        min_length=3,
        max_length=1000,
        examples=[
            "Find customers who joined after Jan 2023 with more than 5 orders",
            "اعثر على العملاء الذين انضموا بعد يناير 2023"
        ]
    )
    
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate and clean the prompt."""
        v = v.strip()
        if not v:
            raise ValueError("Prompt cannot be empty")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Find female customers in Riyadh with more than 1000 sales"
                },
                {
                    "prompt": "اعثر على العملاء الذين لديهم أكثر من 10 طلبات"
                }
            ]
        }
    }

