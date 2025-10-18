"""LangSmith observability and tracing integration."""

import os
from typing import Dict, Any, Optional
from contextlib import contextmanager
from langsmith import Client
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class ObservabilityManager:
    """Manages LangSmith tracing and observability."""
    
    def __init__(self):
        """Initialize the observability manager."""
        self.settings = get_settings()
        self.client: Optional[Client] = None
        
        # Initialize LangSmith client if tracing is enabled
        if self.settings.langchain_tracing_v2 and self.settings.langchain_api_key:
            try:
                self.client = Client(
                    api_key=self.settings.langchain_api_key,
                    api_url=self.settings.langchain_endpoint,
                )
                logger.info("LangSmith client initialized", project=self.settings.langchain_project)
            except Exception as e:
                logger.warning("Failed to initialize LangSmith client", error=str(e))
                self.client = None
        else:
            logger.info("LangSmith tracing disabled")
    
    def setup_environment(self) -> None:
        """Setup environment variables for LangChain tracing."""
        if self.settings.langchain_tracing_v2:
            os.environ["LANGCHAIN_TRACING_V2"] = str(self.settings.langchain_tracing_v2).lower()
            os.environ["LANGCHAIN_ENDPOINT"] = self.settings.langchain_endpoint
            os.environ["LANGCHAIN_PROJECT"] = self.settings.langchain_project
            
            if self.settings.langchain_api_key:
                os.environ["LANGCHAIN_API_KEY"] = self.settings.langchain_api_key
    
    @contextmanager
    def trace_run(self, run_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for tracing a run.
        
        Args:
            run_name: Name of the run to trace
            metadata: Additional metadata to attach to the run
            
        Yields:
            None
        """
        # Setup environment for this run
        self.setup_environment()
        
        logger.info("Starting traced run", run_name=run_name, metadata=metadata)
        
        try:
            yield
        except Exception as e:
            logger.error("Traced run failed", run_name=run_name, error=str(e))
            raise
        finally:
            logger.info("Traced run completed", run_name=run_name)
    
    def log_prompt(self, prompt: str, language: str) -> None:
        """Log the input prompt.
        
        Args:
            prompt: The user prompt
            language: Detected language (en/ar)
        """
        logger.info("Prompt received", prompt=prompt[:200], language=language)
    
    def log_parsing_result(self, raw_filters: list, success: bool) -> None:
        """Log the parsing result.
        
        Args:
            raw_filters: Extracted filters
            success: Whether parsing was successful
        """
        logger.info(
            "Parsing result",
            filter_count=len(raw_filters),
            success=success,
            filters=raw_filters,
        )
    
    def log_validation_result(
        self, validated_filters: list, errors: list, success: bool
    ) -> None:
        """Log the validation result.
        
        Args:
            validated_filters: Validated filters
            errors: Validation errors
            success: Whether validation was successful
        """
        logger.info(
            "Validation result",
            validated_count=len(validated_filters),
            error_count=len(errors),
            success=success,
            errors=errors if errors else None,
        )
    
    def log_final_output(self, output: Dict[str, Any]) -> None:
        """Log the final output.
        
        Args:
            output: The final output dictionary
        """
        logger.info(
            "Final output",
            filter_count=len(output.get("filters", [])),
            has_errors="errors" in output,
        )


# Global instance
_observability_manager: Optional[ObservabilityManager] = None


def get_observability_manager() -> ObservabilityManager:
    """Get or create the observability manager instance.
    
    Returns:
        ObservabilityManager instance
    """
    global _observability_manager
    if _observability_manager is None:
        _observability_manager = ObservabilityManager()
    return _observability_manager

