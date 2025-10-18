"""Test cases for Arabic prompt parsing."""

import pytest
import json
from pathlib import Path
from app.agent import build_agent_graph


@pytest.fixture(scope="module")
def agent_graph():
    """Create an agent graph for testing."""
    return build_agent_graph()


@pytest.fixture(scope="module")
def test_dataset():
    """Load the test dataset."""
    dataset_path = Path(__file__).parent / "dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestArabicParsing:
    """Test cases for parsing Arabic prompts."""
    
    def test_simple_gender_filter_ar(self, agent_graph):
        """Test parsing a simple Arabic gender filter."""
        result = agent_graph.invoke({"prompt": "اعثر على العملاء الإناث"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        gender_filter = next((f for f in filters if f["field"] == "gender"), None)
        assert gender_filter is not None
        assert gender_filter["operator"] == "="
        assert gender_filter["value"] in ["Female", "female"]
    
    def test_greater_than_orders_ar(self, agent_graph):
        """Test parsing Arabic greater than operator."""
        result = agent_graph.invoke({"prompt": "العملاء الذين لديهم أكثر من 10 طلبات"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        orders_filter = next((f for f in filters if f["field"] == "total_orders"), None)
        assert orders_filter is not None
        assert orders_filter["operator"] == ">"
        assert orders_filter["value"] == 10
    
    def test_between_rating_ar(self, agent_graph):
        """Test parsing Arabic between operator."""
        result = agent_graph.invoke({"prompt": "المتاجر التي تقييمها بين 3 و 5 نجوم"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        rating_filter = next((f for f in filters if f["field"] == "store_rating"), None)
        assert rating_filter is not None
        assert rating_filter["operator"] == "between"
        assert isinstance(rating_filter["value"], list)
        assert len(rating_filter["value"]) == 2
    
    def test_city_filter_ar(self, agent_graph):
        """Test parsing Arabic city filter."""
        result = agent_graph.invoke({"prompt": "العملاء في الرياض الذين لديهم أكثر من 500 مبيعات"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 2
        
        city_filter = next((f for f in filters if f["field"] == "city"), None)
        assert city_filter is not None
        assert city_filter["operator"] == "="
        assert "Riyadh" in str(city_filter["value"]) or "الرياض" in str(city_filter["value"])
    
    def test_male_customers_ar(self, agent_graph):
        """Test parsing male customers in Arabic."""
        result = agent_graph.invoke({"prompt": "العملاء الذكور"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        gender_filter = next((f for f in filters if f["field"] == "gender"), None)
        assert gender_filter is not None
        assert gender_filter["value"] in ["Male", "male"]


@pytest.mark.parametrize("test_case_id", [1, 2, 3, 4, 5, 6, 9, 11])
def test_dataset_cases_ar(agent_graph, test_dataset, test_case_id):
    """Test Arabic prompts from the dataset.
    
    Note: This is a flexible test that checks for reasonable filter extraction,
    not exact matching, since LLM output may vary.
    """
    test_case = next((tc for tc in test_dataset["test_cases"] if tc["id"] == test_case_id), None)
    assert test_case is not None, f"Test case {test_case_id} not found"
    
    prompt = test_case["prompt_ar"]
    expected = test_case["expected_output"]["filters"]
    
    result = agent_graph.invoke({"prompt": prompt})
    output = result.get("output", {})
    filters = output.get("filters", [])
    
    # Check that we got at least some filters
    assert len(filters) > 0, f"No filters extracted for: {prompt}"
    
    # Check that key fields are present
    expected_fields = {f["field"] for f in expected}
    actual_fields = {f["field"] for f in filters}
    
    # At least one expected field should be present
    assert len(expected_fields & actual_fields) > 0, \
        f"Expected fields {expected_fields} but got {actual_fields} for prompt: {prompt}"

