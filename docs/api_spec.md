# API Specification

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently no authentication required. For production deployment, implement API key authentication via API Gateway.

## Endpoints

### 1. Health Check

#### `GET /health`

Returns the health status of the service.

**Response**
```json
{
  "status": "healthy",
  "service": "ai-audience-agent"
}
```

**Status Codes**
- `200 OK`: Service is healthy

---

### 2. Root Information

#### `GET /`

Returns basic information about the API.

**Response**
```json
{
  "name": "AI Audience Agent",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

**Status Codes**
- `200 OK`: Successfully retrieved information

---

### 3. Parse Prompt

#### `POST /api/v1/parse_prompt`

Converts a natural language prompt into structured audience filters.

**Request Headers**
```
Content-Type: application/json
```

**Request Body**
```json
{
  "prompt": "Find female customers in Riyadh with more than 1000 sales"
}
```

**Request Schema**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | Natural language prompt (3-1000 characters) |

**Response Body (Success)**
```json
{
  "filters": [
    {
      "field": "gender",
      "operator": "=",
      "value": "Female"
    },
    {
      "field": "city",
      "operator": "=",
      "value": "Riyadh"
    },
    {
      "field": "total_sales",
      "operator": ">",
      "value": 1000
    }
  ]
}
```

**Response Schema**
| Field | Type | Description |
|-------|------|-------------|
| filters | array | Array of filter objects |
| filters[].field | string | Field name to filter on |
| filters[].operator | string | Comparison operator (=, !=, <, >, <=, >=, between) |
| filters[].value | string\|number\|boolean\|array | Filter value(s) |

**Status Codes**
- `200 OK`: Successfully parsed prompt
- `400 Bad Request`: Invalid prompt or parsing error
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server error

**Error Response**
```json
{
  "error": "The field 'email_open_rate' is not supported",
  "details": {
    "field": "email_open_rate",
    "supported_fields": ["gender", "total_orders", "..."]
  }
}
```

---

## Examples

### Example 1: Simple Gender Filter (English)

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find female customers"}'
```

**Response**
```json
{
  "filters": [
    {
      "field": "gender",
      "operator": "=",
      "value": "Female"
    }
  ]
}
```

### Example 2: Simple Gender Filter (Arabic)

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "اعثر على العملاء الإناث"}'
```

**Response**
```json
{
  "filters": [
    {
      "field": "gender",
      "operator": "=",
      "value": "Female"
    }
  ]
}
```

### Example 3: Multiple Filters (English)

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find customers who joined after Jan 2023 with more than 5 orders and store rating between 3 and 5"}'
```

**Response**
```json
{
  "filters": [
    {
      "field": "joining_date",
      "operator": ">",
      "value": "2023-01-01"
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
```

### Example 4: Complex Query (Arabic)

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "العملاء في الرياض الذين لديهم أكثر من 500 مبيعات"}'
```

**Response**
```json
{
  "filters": [
    {
      "field": "city",
      "operator": "=",
      "value": "Riyadh"
    },
    {
      "field": "total_sales",
      "operator": ">",
      "value": 500
    }
  ]
}
```

### Example 5: Between Operator

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Stores rated between 3 and 5 stars"}'
```

**Response**
```json
{
  "filters": [
    {
      "field": "store_rating",
      "operator": "between",
      "value": [3, 5]
    }
  ]
}
```

### Example 6: Error - Unsupported Field

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find customers with email open rate above 50%"}'
```

**Response (400 Bad Request)**
```json
{
  "error": "Failed to parse prompt into valid filters",
  "details": {
    "errors": [
      "Filter 1: Unsupported field: email_open_rate"
    ]
  }
}
```

### Example 7: Error - Empty Prompt

**Request**
```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": ""}'
```

**Response (422 Unprocessable Entity)**
```json
{
  "error": "Request validation failed",
  "details": {
    "errors": [
      {
        "type": "string_too_short",
        "loc": ["body", "prompt"],
        "msg": "String should have at least 3 characters"
      }
    ]
  }
}
```

---

## OpenAPI/Swagger Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Supported Fields

### Customer Attributes
- `gender` - Customer gender (Male/Female)
- `birthday` - Date of birth (YYYY-MM-DD)
- `birthday_days` - Birthday within N days
- `joining_date` - Account creation date (YYYY-MM-DD)
- `last_login` - Last login date (YYYY-MM-DD)

### Behavioral Attributes
- `doesnt_have_orders` - Customer has no orders (boolean)
- `have_cancelled_orders` - Customer has cancelled orders (boolean)
- `latest_purchase` - Date of most recent purchase (YYYY-MM-DD)

### Sales & Engagement
- `total_sales` - Total sales amount (number)
- `total_orders` - Number of orders (integer)
- `store_rating` - Customer rating of store (1-5)

### Contact Attributes
- `doesnt_have_email` - Customer has no email address (boolean)

### Geographic Attributes
- `country` - Customer country
- `city` - Customer city

---

## Supported Operators

| Operator | Description | Example Value |
|----------|-------------|---------------|
| `=` | Equals | `"Female"`, `5` |
| `!=` | Not equals | `"Male"`, `1` |
| `<` | Less than | `100`, `"2023-01-01"` |
| `>` | Greater than | `1000`, `"2022-12-31"` |
| `<=` | Less than or equal | `50` |
| `>=` | Greater than or equal | `1000` |
| `between` | Range (inclusive) | `[3, 5]`, `[1000, 5000]` |

---

## Rate Limiting

Currently no rate limiting. Recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## CORS

Default configuration allows all origins (`*`). Configure appropriately for production in `app/main.py`.

