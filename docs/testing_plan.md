# Testing Plan

## Overview

This document outlines the comprehensive testing strategy for the AI Audience Agent, including test coverage, validation metrics, and continuous improvement processes.

## Test Coverage

### 1. Unit Tests

#### Core Utils (`app/tests/test_validation.py`)

**Field Normalization**
- Test field name aliases (e.g., "sex" → "gender")
- Test order field variants
- Test sales/revenue normalization
- Test unchanged field names

**Operator Normalization**
- Test equals variants ("equals", "is", "=")
- Test not equals ("not equal", "is not", "!=")
- Test comparison operators ("greater than", ">", "gt")
- Test between operator variants

**Value Normalization**
- Test gender value mapping (including Arabic)
- Test city/country translations
- Test numeric value conversion
- Test boolean mappings
- Test date parsing

**Filter Validation**
- Test valid filter acceptance
- Test invalid field rejection
- Test invalid operator rejection
- Test missing value detection
- Test between operator validation
- Test operator compatibility with field types

### 2. Integration Tests

#### English Parsing (`app/tests/test_parser_en.py`)

**Test Cases**
- Simple gender filter
- Greater than operator (orders)
- Between operator (ratings)
- Multiple filters in one prompt
- City and location filters
- Less than operator
- Greater than or equal operator
- Complex multi-filter scenarios

**Dataset Tests**
- Parametrized tests using `dataset.json`
- Tests IDs 1-8 covering various scenarios
- Flexible validation (checks for key fields, not exact match)

#### Arabic Parsing (`app/tests/test_parser_ar.py`)

**Test Cases**
- Simple gender filter (Arabic)
- Greater than operator (Arabic)
- Between operator (Arabic)
- City filters with Arabic names
- Male customers (Arabic)

**Dataset Tests**
- Parametrized tests using `dataset.json`
- Tests IDs 1, 2, 3, 4, 5, 6, 9, 11
- Language-specific validation

### 3. API Tests

#### Endpoint Testing
```python
# Example API test structure
def test_parse_prompt_endpoint():
    response = client.post(
        "/api/v1/parse_prompt",
        json={"prompt": "Find female customers"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "filters" in data
    assert len(data["filters"]) > 0
```

**Scenarios to Test**
- Valid English prompts
- Valid Arabic prompts
- Empty prompts
- Invalid prompts
- Very long prompts
- Special characters
- Error handling

## Test Dataset

### Structure

The test dataset (`app/tests/dataset.json`) contains 20+ bilingual test cases:

```json
{
  "id": 1,
  "prompt_en": "English prompt",
  "prompt_ar": "Arabic prompt",
  "expected_output": {
    "filters": [...]
  }
}
```

### Coverage Matrix

| ID | Type | Fields Tested | Operators | Languages |
|----|------|---------------|-----------|-----------|
| 1 | Simple | gender | = | EN, AR |
| 2 | Simple | total_orders | > | EN, AR |
| 3 | Range | store_rating | between | EN, AR |
| 4 | Complex | joining_date, total_orders, store_rating | >, between | EN, AR |
| 5 | Geographic | city, total_sales | =, > | EN, AR |
| 6 | Simple | gender | = | EN, AR |
| 7 | Comparison | total_sales | >= | EN, AR |
| 8 | Comparison | total_orders | < | EN, AR |
| 9 | Geographic | country | = | EN, AR |
| 10 | Multi-value | city | = | EN, AR |
| 11 | Date | joining_date | < | EN, AR |
| 12 | Exact | store_rating | = | EN, AR |
| 13 | Comparison | total_sales | <= | EN, AR |
| 14 | Complex | gender, city, total_orders | =, > | EN, AR |
| 15 | Boolean | doesnt_have_email | = | EN, AR |
| 16 | Boolean | doesnt_have_orders | = | EN, AR |
| 17 | Boolean | have_cancelled_orders | = | EN, AR |
| 18 | Negation | store_rating | != | EN, AR |
| 19 | Very Complex | gender, city, total_sales | =, between | EN, AR |
| 20 | Geographic | country | = | EN, AR |

## Running Tests

### Setup

```bash
# Navigate to project directory
cd ai_audience_agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here
export LANGCHAIN_TRACING_V2=false  # Optional for tests
```

### Run All Tests

```bash
pytest app/tests/
```

### Run Specific Test Suites

```bash
# English parsing tests only
pytest app/tests/test_parser_en.py

# Arabic parsing tests only
pytest app/tests/test_parser_ar.py

# Validation tests only
pytest app/tests/test_validation.py
```

### Run with Coverage

```bash
pytest app/tests/ --cov=app --cov-report=html
```

### Run Specific Test Case

```bash
pytest app/tests/test_parser_en.py::TestEnglishParsing::test_simple_gender_filter
```

## Validation Metrics

### 1. Accuracy Metrics

**Definition**: Percentage of prompts correctly parsed into valid filters

**Calculation**:
```python
accuracy = (correctly_parsed / total_prompts) * 100
```

**Target**: ≥ 90%

**Measurement**:
- Use the evaluation script: `scripts/evaluate_accuracy.py`
- Test against full dataset (50-100 cases)
- Separate metrics for English and Arabic

### 2. Field Extraction Accuracy

**Definition**: Percentage of expected fields correctly identified

**Calculation**:
```python
field_accuracy = (correct_fields / expected_fields) * 100
```

**Target**: ≥ 95%

### 3. Operator Accuracy

**Definition**: Percentage of operators correctly assigned

**Calculation**:
```python
operator_accuracy = (correct_operators / total_filters) * 100
```

**Target**: ≥ 95%

### 4. Value Normalization Accuracy

**Definition**: Percentage of values correctly normalized

Examples:
- "male" → "Male"
- "الرياض" → "Riyadh"
- "Jan 2023" → "2023-01-01"

**Target**: ≥ 90%

### 5. Performance Metrics

**Response Time**:
- Target: < 2 seconds average
- Max acceptable: < 5 seconds

**Throughput**:
- Target: 100 requests/minute
- Measure with load testing

## Error Analysis

### Error Categories

1. **Field Recognition Errors**
   - Unsupported field mentioned
   - Field alias not recognized
   - Field completely missed

2. **Operator Errors**
   - Wrong operator chosen
   - Operator not normalized correctly
   - Invalid operator for field type

3. **Value Extraction Errors**
   - Value not extracted
   - Value incorrectly parsed
   - Value not normalized

4. **Complex Query Errors**
   - Missing filters in multi-filter prompts
   - Incorrect filter combination
   - Ambiguous intent misinterpreted

### Error Tracking

Log all errors in LangSmith with:
- Input prompt
- Expected output
- Actual output
- Error type
- Error message

## Continuous Improvement

### 1. Error Feedback Loop

```
User Report → Manual Review → Add to Test Dataset → Re-train/Adjust → Validate
```

### 2. Prompt Engineering Iteration

- Refine system prompts based on failure patterns
- Add more examples for problematic cases
- Improve field descriptions

### 3. Dataset Enhancement

- Add new test cases for edge cases
- Include real user prompts (anonymized)
- Expand to 100+ test cases over time

### 4. Model Updates

- Test with different LLM models
- Compare GPT-3.5 vs GPT-4 performance
- Consider fine-tuning for specific use case

## Automated Testing Pipeline

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Test AI Audience Agent

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: pytest app/tests/ --cov=app
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-deployment Validation

Before deploying to production:
1. Run full test suite
2. Calculate accuracy metrics
3. Review LangSmith traces for anomalies
4. Perform manual testing of edge cases
5. Load test for performance validation

## Success Criteria

✅ **Must Pass**:
- All unit tests passing
- Accuracy ≥ 90% on test dataset
- No critical errors in validation
- Performance < 2s average response time

⚠️ **Warning Thresholds**:
- Accuracy 85-90%
- Performance 2-5s response time
- More than 5% validation errors

❌ **Failure Conditions**:
- Accuracy < 85%
- Performance > 5s average
- Critical security vulnerabilities
- More than 10% validation errors

## Reporting

### Test Reports

Generate after each test run:
```bash
pytest app/tests/ --html=report.html --self-contained-html
```

### Accuracy Reports

Run evaluation script:
```bash
python scripts/evaluate_accuracy.py --output report.json
```

### Dashboard Metrics

Track in LangSmith dashboard:
- Total requests
- Success rate
- Average response time
- Error rate by category
- Most common errors

## Future Testing Enhancements

1. **Adversarial Testing**: Test with intentionally ambiguous prompts
2. **Multilingual Expansion**: Add more Arabic dialects, add other languages
3. **Performance Testing**: Load testing with concurrent requests
4. **Security Testing**: Input sanitization, injection attacks
5. **A/B Testing**: Compare different prompt strategies
6. **User Acceptance Testing**: Real user feedback integration

