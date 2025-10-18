"""Test cases for filter validation."""

import pytest
from app.agent.utils import (
    normalize_field_name,
    normalize_operator,
    normalize_value,
    validate_filter,
    load_supported_fields,
)


class TestFieldNormalization:
    """Test field name normalization."""
    
    def test_normalize_gender_alias(self):
        """Test normalizing gender field aliases."""
        assert normalize_field_name("sex") == "gender"
        assert normalize_field_name("Sex") == "gender"
        assert normalize_field_name("SEX") == "gender"
    
    def test_normalize_order_aliases(self):
        """Test normalizing order field aliases."""
        assert normalize_field_name("orders") == "total_orders"
        assert normalize_field_name("order_count") == "total_orders"
        assert normalize_field_name("num_orders") == "total_orders"
    
    def test_normalize_sales_aliases(self):
        """Test normalizing sales field aliases."""
        assert normalize_field_name("sales") == "total_sales"
        assert normalize_field_name("revenue") == "total_sales"
    
    def test_normalize_unchanged(self):
        """Test that valid fields remain unchanged."""
        assert normalize_field_name("gender") == "gender"
        assert normalize_field_name("total_orders") == "total_orders"


class TestOperatorNormalization:
    """Test operator normalization."""
    
    def test_normalize_equals_variants(self):
        """Test normalizing equals operator variants."""
        assert normalize_operator("equals") == "="
        assert normalize_operator("equal") == "="
        assert normalize_operator("is") == "="
        assert normalize_operator("=") == "="
    
    def test_normalize_not_equals(self):
        """Test normalizing not equals variants."""
        assert normalize_operator("not equals") == "!="
        assert normalize_operator("not equal") == "!="
        assert normalize_operator("is not") == "!="
    
    def test_normalize_comparison_operators(self):
        """Test normalizing comparison operators."""
        assert normalize_operator("greater than") == ">"
        assert normalize_operator("more than") == ">"
        assert normalize_operator("gt") == ">"
        assert normalize_operator("less than") == "<"
        assert normalize_operator("lt") == "<"
        assert normalize_operator("at least") == ">="
        assert normalize_operator("gte") == ">="
        assert normalize_operator("at most") == "<="
        assert normalize_operator("lte") == "<="
    
    def test_normalize_between(self):
        """Test normalizing between operator."""
        assert normalize_operator("between") == "between"
        assert normalize_operator("in range") == "between"
        assert normalize_operator("range") == "between"


class TestValueNormalization:
    """Test value normalization."""
    
    def test_normalize_gender_values(self):
        """Test normalizing gender values."""
        assert normalize_value("gender", "male", "string") == "Male"
        assert normalize_value("gender", "female", "string") == "Female"
        assert normalize_value("gender", "m", "string") == "Male"
        assert normalize_value("gender", "f", "string") == "Female"
        assert normalize_value("gender", "ذكر", "string") == "Male"
        assert normalize_value("gender", "انثى", "string") == "Female"
    
    def test_normalize_city_values(self):
        """Test normalizing city values."""
        assert normalize_value("city", "الرياض", "string") == "Riyadh"
        assert normalize_value("city", "جدة", "string") == "Jeddah"
        assert normalize_value("city", "دبي", "string") == "Dubai"
    
    def test_normalize_numeric_values(self):
        """Test normalizing numeric values."""
        assert normalize_value("total_orders", "10", "integer") == 10
        assert normalize_value("total_orders", 10.5, "integer") == 10
        assert normalize_value("total_sales", "100.5", "float") == 100.5
        assert normalize_value("total_sales", 100, "float") == 100.0
    
    def test_normalize_unchanged_values(self):
        """Test that some values remain unchanged."""
        assert normalize_value("total_orders", 5, "integer") == 5
        assert normalize_value("store_rating", 4.5, "float") == 4.5


class TestFilterValidation:
    """Test filter validation."""
    
    def test_valid_filter(self):
        """Test validating a valid filter."""
        config = load_supported_fields()
        filter_dict = {
            "field": "gender",
            "operator": "=",
            "value": "Female"
        }
        errors = validate_filter(filter_dict, config)
        assert len(errors) == 0
    
    def test_invalid_field(self):
        """Test validation with invalid field."""
        config = load_supported_fields()
        filter_dict = {
            "field": "invalid_field",
            "operator": "=",
            "value": "test"
        }
        errors = validate_filter(filter_dict, config)
        assert len(errors) > 0
        assert any("Unsupported field" in error for error in errors)
    
    def test_invalid_operator(self):
        """Test validation with invalid operator."""
        config = load_supported_fields()
        filter_dict = {
            "field": "gender",
            "operator": "invalid_op",
            "value": "Female"
        }
        errors = validate_filter(filter_dict, config)
        assert len(errors) > 0
        assert any("Unsupported operator" in error for error in errors)
    
    def test_missing_value(self):
        """Test validation with missing value."""
        config = load_supported_fields()
        filter_dict = {
            "field": "gender",
            "operator": "=",
            "value": ""
        }
        errors = validate_filter(filter_dict, config)
        assert len(errors) > 0
        assert any("Missing value" in error for error in errors)
    
    def test_between_with_invalid_value(self):
        """Test validation of between operator with non-list value."""
        config = load_supported_fields()
        filter_dict = {
            "field": "store_rating",
            "operator": "between",
            "value": 5
        }
        errors = validate_filter(filter_dict, config)
        assert len(errors) > 0
        assert any("list of two values" in error for error in errors)
    
    def test_between_with_valid_value(self):
        """Test validation of between operator with valid list."""
        config = load_supported_fields()
        filter_dict = {
            "field": "store_rating",
            "operator": "between",
            "value": [3, 5]
        }
        errors = validate_filter(filter_dict, config)
        # Should have no errors or minimal errors not related to between validation
        assert not any("list of two values" in error for error in errors)
    
    def test_invalid_operator_for_field_type(self):
        """Test validation with operator invalid for field type."""
        config = load_supported_fields()
        # String fields shouldn't support > operator
        filter_dict = {
            "field": "gender",
            "operator": ">",
            "value": "Female"
        }
        errors = validate_filter(filter_dict, config)
        assert len(errors) > 0
        # Should have error about operator not valid for field type

