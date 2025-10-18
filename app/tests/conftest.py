"""Pytest configuration and shared fixtures."""

import os
import pytest
from pathlib import Path


# Set test environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["DEBUG"] = "false"


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent.parent.parent / "data"


@pytest.fixture(scope="session")
def test_dataset_path():
    """Return the path to the test dataset."""
    return Path(__file__).parent / "dataset.json"


@pytest.fixture(scope="module")
def sample_prompts():
    """Return sample prompts for testing."""
    return {
        "en": {
            "simple": "Find female customers",
            "complex": "Find customers who joined after Jan 2023 with more than 5 orders",
            "with_city": "Customers in Riyadh with more than 500 sales",
        },
        "ar": {
            "simple": "اعثر على العملاء الإناث",
            "complex": "اعثر على العملاء الذين انضموا بعد يناير 2023 ولديهم أكثر من 5 طلبات",
            "with_city": "العملاء في الرياض الذين لديهم أكثر من 500 مبيعات",
        }
    }


@pytest.fixture
def sample_filters():
    """Return sample filter structures."""
    return {
        "gender": {"field": "gender", "operator": "=", "value": "Female"},
        "orders_gt": {"field": "total_orders", "operator": ">", "value": 10},
        "rating_between": {"field": "store_rating", "operator": "between", "value": [3, 5]},
        "city": {"field": "city", "operator": "=", "value": "Riyadh"},
    }


@pytest.fixture
def mock_config():
    """Return mock configuration for testing."""
    return {
        "fields": {
            "customer_attributes": ["gender", "joining_date"],
            "sales_engagement": ["total_orders", "store_rating"],
            "geographic_attributes": ["city", "country"],
        },
        "operators": ["=", "!=", "<", ">", "<=", ">=", "between"],
        "field_types": {
            "gender": "string",
            "joining_date": "date",
            "total_orders": "integer",
            "store_rating": "float",
            "city": "string",
        }
    }

