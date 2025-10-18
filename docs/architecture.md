# AI Audience Agent - Architecture

## Overview

The AI Audience Agent is a sophisticated system that converts natural language prompts (in English or Arabic) into structured audience filters using LangGraph orchestration, LangChain LLMs, and LangSmith observability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FastAPI Server                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    POST /parse_prompt                      │  │
│  └───────────────────────────────┬───────────────────────────┘  │
└────────────────────────────────┬─┴──────────────────────────────┘
                                 │
                    ┌────────────▼───────────┐
                    │   LangGraph Workflow   │
                    └────────────┬───────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐      ┌───────▼────────┐      ┌───────▼────────┐
│  Input Node    │─────▶│  Parsing Node  │─────▶│Validation Node │
│                │      │                │      │                │
│ • Receives     │      │ • LLM Extract  │      │ • Validates    │
│   prompt       │      │ • Structured   │      │   fields       │
│ • Detects      │      │   filters      │      │ • Normalizes   │
│   language     │      │                │      │   values       │
└────────────────┘      └────────────────┘      └────────┬───────┘
                                                          │
                                                 ┌────────▼────────┐
                                                 │  Output Node    │
                                                 │                 │
                                                 │ • Formats       │
                                                 │   response      │
                                                 │ • Returns JSON  │
                                                 └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     LangSmith Observability                      │
│  • Traces all node executions                                    │
│  • Logs inputs, outputs, errors                                  │
│  • Performance metrics                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. FastAPI Application (`app/main.py`)

The FastAPI server provides:
- REST API endpoint for prompt parsing
- Request validation using Pydantic schemas
- Error handling and logging
- Health check endpoints
- CORS middleware for cross-origin requests

### 2. LangGraph Agent (`app/agent/`)

The core of the system, consisting of four nodes:

#### Input Node (`nodes/input_node.py`)
- Receives the user prompt
- Detects language (English or Arabic)
- Prepares initial state

#### Parsing Node (`nodes/parsing_node.py`)
- Uses OpenAI GPT-4 to extract filters
- Converts natural language to structured format
- Handles both English and Arabic prompts
- Uses Pydantic output parser for structure

#### Validation Node (`nodes/validation_node.py`)
- Validates extracted filters against supported fields
- Normalizes field names, operators, and values
- Applies value mappings (e.g., "الرياض" → "Riyadh")
- Ensures operator compatibility with field types

#### Output Node (`nodes/output_node.py`)
- Formats validated filters into final JSON response
- Includes error information if validation failed

### 3. Observability (`app/agent/observability.py`)

LangSmith integration provides:
- Full tracing of agent execution
- Logging of inputs, outputs, and errors
- Performance monitoring
- Debugging capabilities

### 4. Configuration Management (`app/core/`)

- **config.py**: Environment-based configuration
- **logger.py**: Structured logging with structlog
- **errors.py**: Custom exception hierarchy

### 5. Data Layer (`data/`)

- **supported_fields.json**: Field definitions and operator mappings
- **value_mappings.json**: Normalization rules for values
- **examples_en_ar.json**: Example prompts and expected outputs

## Data Flow

1. **Request Reception**
   ```
   POST /api/v1/parse_prompt
   Body: { "prompt": "Find female customers in Riyadh" }
   ```

2. **Input Processing**
   - Language detection
   - Initial state preparation

3. **LLM Parsing**
   - Prompt sent to GPT-4 with context
   - Structured filters extracted using Pydantic parser

4. **Validation & Normalization**
   - Field names normalized (e.g., "orders" → "total_orders")
   - Operators standardized (e.g., "more than" → ">")
   - Values normalized (e.g., "female" → "Female")
   - Invalid filters rejected with error messages

5. **Response Formation**
   ```json
   {
     "filters": [
       { "field": "gender", "operator": "=", "value": "Female" },
       { "field": "city", "operator": "=", "value": "Riyadh" }
     ]
   }
   ```

## Supported Fields

### Customer Attributes
- `gender`, `birthday`, `birthday_days`, `joining_date`, `last_login`

### Behavioral Attributes
- `doesnt_have_orders`, `have_cancelled_orders`, `latest_purchase`

### Sales & Engagement
- `total_sales`, `total_orders`, `store_rating`

### Contact Attributes
- `doesnt_have_email`

### Geographic Attributes
- `country`, `city`

## Supported Operators

- `=` (equals)
- `!=` (not equals)
- `<` (less than)
- `>` (greater than)
- `<=` (less than or equal)
- `>=` (greater than or equal)
- `between` (range, requires list value)

## Error Handling

The system provides specific error messages for:
- Unsupported fields
- Invalid operators
- Missing values
- Type mismatches
- Ambiguous dates

Example error response:
```json
{
  "error": "The field 'email_open_rate' is not supported",
  "details": {
    "field": "email_open_rate",
    "supported_fields": ["gender", "total_orders", "..."]
  }
}
```

## Deployment Architecture

### Local Development
```
uvicorn app.main:app --reload
```

### Docker Container
```
docker-compose up
```

### Production (Cloud)
- AWS ECS / Fargate
- GCP Cloud Run
- Azure App Service
- Behind API Gateway with authentication

## Monitoring & Observability

### LangSmith Dashboard
- View all parsing requests
- Trace execution through nodes
- Debug failures
- Monitor performance metrics

### Application Logs
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Error tracking

## Security Considerations

1. **API Key Management**: OpenAI and LangSmith keys stored in environment variables
2. **Input Validation**: Pydantic schemas validate all inputs
3. **Rate Limiting**: Recommended for production
4. **CORS**: Configure allowed origins for production
5. **Authentication**: Add API Gateway authentication

## Performance

- **Target Response Time**: < 2 seconds
- **Accuracy Goal**: ≥ 90% correct parsing
- **Scalability**: Horizontal scaling via container orchestration

## Future Enhancements

1. Caching layer for common prompts
2. Batch processing endpoint
3. Additional language support
4. Custom field definitions via API
5. Learning from user corrections

