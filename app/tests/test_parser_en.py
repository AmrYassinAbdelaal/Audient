"""Test cases for English prompt parsing."""

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


class TestEnglishParsing:
    """Test cases for parsing English prompts."""
    
    def test_simple_gender_filter(self, agent_graph):
        """Test parsing a simple gender filter."""
        result = agent_graph.invoke({"prompt": "Find female customers"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        gender_filter = next((f for f in filters if f["field"] == "gender"), None)
        assert gender_filter is not None
        assert gender_filter["operator"] == "="
        assert gender_filter["value"] in ["Female", "female"]
    
    def test_greater_than_orders(self, agent_graph):
        """Test parsing greater than operator."""
        result = agent_graph.invoke({"prompt": "Customers with more than 10 orders"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        orders_filter = next((f for f in filters if f["field"] == "total_orders"), None)
        assert orders_filter is not None
        assert orders_filter["operator"] == ">"
        assert orders_filter["value"] == 10
    
    def test_between_rating(self, agent_graph):
        """Test parsing between operator."""
        result = agent_graph.invoke({"prompt": "Stores rated between 3 and 5 stars"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        rating_filter = next((f for f in filters if f["field"] == "store_rating"), None)
        assert rating_filter is not None
        assert rating_filter["operator"] == "between"
        assert isinstance(rating_filter["value"], list)
        assert len(rating_filter["value"]) == 2
    
    def test_multiple_filters(self, agent_graph):
        """Test parsing multiple filters from one prompt."""
        prompt = "Find customers who joined after Jan 2023 with more than 5 orders"
        result = agent_graph.invoke({"prompt": prompt})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 2
        
        # Check for joining_date filter
        date_filter = next((f for f in filters if f["field"] == "joining_date"), None)
        assert date_filter is not None
        
        # Check for total_orders filter
        orders_filter = next((f for f in filters if f["field"] == "total_orders"), None)
        assert orders_filter is not None
    
    def test_city_filter(self, agent_graph):
        """Test parsing city filter."""
        result = agent_graph.invoke({"prompt": "Customers in Riyadh with more than 500 sales"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 2
        
        city_filter = next((f for f in filters if f["field"] == "city"), None)
        assert city_filter is not None
        assert city_filter["operator"] == "="
        assert "Riyadh" in str(city_filter["value"])
    
    def test_less_than_operator(self, agent_graph):
        """Test parsing less than operator."""
        result = agent_graph.invoke({"prompt": "Customers with less than 3 orders"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        orders_filter = next((f for f in filters if f["field"] == "total_orders"), None)
        assert orders_filter is not None
        assert orders_filter["operator"] == "<"
        assert orders_filter["value"] == 3
    
    def test_greater_than_equal(self, agent_graph):
        """Test parsing greater than or equal operator."""
        result = agent_graph.invoke({"prompt": "Customers with total sales greater than or equal to 1000"})
        output = result.get("output", {})
        filters = output.get("filters", [])
        
        assert len(filters) >= 1
        sales_filter = next((f for f in filters if f["field"] == "total_sales"), None)
        assert sales_filter is not None
        assert sales_filter["operator"] in [">=", ">"]
        assert sales_filter["value"] >= 1000


@pytest.mark.parametrize("test_case_id", [1, 2, 3, 4, 5, 6, 7, 8])
def test_dataset_cases_en(agent_graph, test_dataset, test_case_id):
    """Test English prompts from the dataset.
    
    Note: This is a flexible test that checks for reasonable filter extraction,
    not exact matching, since LLM output may vary.
    """
    test_case = next((tc for tc in test_dataset["test_cases"] if tc["id"] == test_case_id), None)
    assert test_case is not None, f"Test case {test_case_id} not found"
    
    prompt = test_case["prompt_en"]
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

