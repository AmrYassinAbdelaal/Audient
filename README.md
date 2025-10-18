# Audient

Audience Intelligence: Talk audience, think data.
> AI-powered agent that converts natural language prompts (English & Arabic) into structured audience filters using LangGraph, LangChain, and LangSmith.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.6-blue.svg)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Audient is an intelligent system that converts natural language prompts into structured filters for campaign audience creation. It supports both English and Arabic, leveraging:

- **LangGraph** for agent orchestration
- **LangChain** for LLM integration (OpenAI GPT-4)
- **LangSmith** for observability and tracing
- **FastAPI** for REST API deployment

### Example

**Input (English):**
```
Find customers who joined after Jan 2023 with more than 5 orders and store rating between 3 and 5
```

**Input (Arabic):**
```
اعثر على العملاء الذين انضموا بعد يناير 2023 ولديهم أكثر من 5 طلبات وتقييم المتجر بين 3 و5
```

**Output:**
```json
{
  "filters": [
    { "field": "joining_date", "operator": ">", "value": "2023-01-01" },
    { "field": "total_orders", "operator": ">", "value": 5 },
    { "field": "store_rating", "operator": "between", "value": [3, 5] }
  ]
}
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- (Optional) LangSmith API key for observability

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Audient
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key  # Optional
```

### Running Locally

**Option 1: Using the run script**
```bash
./scripts/run_local.sh
```

**Option 2: Using Make**
```bash
make init
make run
```

**Option 3: Manual start**
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing the API

```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find female customers in Riyadh with more than 1000 sales"}'
```

## 📚 Documentation

- **[Architecture](docs/architecture.md)** - System design and components
- **[API Specification](docs/api_spec.md)** - Detailed API documentation
- **[Testing Plan](docs/testing_plan.md)** - Testing strategy and metrics
- **[Quick Start Guide](QUICKSTART.md)** - 5-minute setup guide
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete project overview

## 🏗️ Project Structure

```
Audient/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   ├── logger.py              # Logging setup
│   │   └── errors.py              # Custom exceptions
│   ├── agent/
│   │   ├── graph_builder.py       # LangGraph workflow definition
│   │   ├── observability.py       # LangSmith integration
│   │   ├── utils.py               # Utility functions
│   │   └── nodes/
│   │       ├── input_node.py      # Input processing
│   │       ├── parsing_node.py    # LLM-based parsing
│   │       ├── validation_node.py # Filter validation
│   │       └── output_node.py     # Response formatting
│   ├── routes/
│   │   └── parse_prompt.py        # API endpoints
│   ├── schemas/
│   │   ├── prompt_schema.py       # Request schemas
│   │   └── filter_schema.py       # Response schemas
│   └── tests/
│       ├── dataset.json           # Test cases (20+ bilingual)
│       ├── test_parser_en.py      # English parsing tests
│       ├── test_parser_ar.py      # Arabic parsing tests
│       └── test_validation.py     # Validation tests
├── data/
│   ├── supported_fields.json      # Field definitions
│   ├── value_mappings.json        # Normalization rules
│   └── examples_en_ar.json        # Sample prompts
├── docker/
│   ├── Dockerfile                 # Container definition
│   └── docker-compose.yml         # Orchestration
├── docs/                          # Documentation
├── scripts/
│   ├── run_local.sh               # Local development script
│   ├── deploy_aws.sh              # AWS deployment script
│   └── evaluate_accuracy.py       # Accuracy evaluation
├── requirements.txt               # Python dependencies
└── README.md
```

## 🔧 Features

### Supported Fields

**Customer Attributes**
- `gender`, `birthday`, `birthday_days`, `joining_date`, `last_login`

**Behavioral Attributes**
- `doesnt_have_orders`, `have_cancelled_orders`, `latest_purchase`

**Sales & Engagement**
- `total_sales`, `total_orders`, `store_rating`

**Contact Attributes**
- `doesnt_have_email`

**Geographic Attributes**
- `country`, `city`

### Supported Operators

- `=` (equals)
- `!=` (not equals)
- `<` (less than)
- `>` (greater than)
- `<=` (less than or equal)
- `>=` (greater than or equal)
- `between` (range)

### Value Types

- **Strings**: `"Female"`, `"Riyadh"`
- **Integers**: `5`, `1000`
- **Floats**: `3.5`, `4.2`
- **Dates**: `"2023-01-01"`, relative dates
- **Lists**: `[3, 5]` for `between` operator
- **Booleans**: `true`, `false`

## 🧪 Testing

### Run All Tests

```bash
pytest app/tests/
```

### Run Specific Tests

```bash
# English tests only
pytest app/tests/test_parser_en.py

# Arabic tests only
pytest app/tests/test_parser_ar.py

# Validation tests
pytest app/tests/test_validation.py
```

### Run with Coverage

```bash
pytest app/tests/ --cov=app --cov-report=html
# or
make test-cov
```

### Evaluate Accuracy

```bash
python scripts/evaluate_accuracy.py --language both --output report.json
# or
make evaluate
```

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build and start
docker-compose -f docker/docker-compose.yml up --build

# Run in detached mode
docker-compose -f docker/docker-compose.yml up -d

# Or use Make
make docker-compose

# Stop
docker-compose -f docker/docker-compose.yml down
```

### Build Docker Image

```bash
docker build -f docker/Dockerfile -t audient:latest .
# or
make docker-build
```

### Run Docker Container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e LANGCHAIN_API_KEY=your_key \
  audient:latest
```

## ☁️ Cloud Deployment

### AWS ECS

```bash
# Configure AWS credentials first
aws configure

# Deploy using the script
export AWS_REGION=us-east-1
export ECR_REPOSITORY=audient
export ECS_CLUSTER=audient-cluster
export ECS_SERVICE=audient-service

./scripts/deploy_aws.sh
```

### GCP Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/audient

# Deploy to Cloud Run
gcloud run deploy audient \
  --image gcr.io/PROJECT_ID/audient \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=your_key
```

### Azure App Service

```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image audient:latest .

# Deploy to App Service
az webapp create --resource-group myResourceGroup \
  --plan myAppServicePlan --name audient \
  --deployment-container-image-name myregistry.azurecr.io/audient:latest
```

## 📊 Observability

### LangSmith Dashboard

1. Sign up at [smith.langchain.com](https://smith.langchain.com)
2. Get your API key
3. Add to `.env`:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=audient
```

4. View traces in the LangSmith dashboard:
   - Request/response logging
   - Node execution traces
   - Error tracking
   - Performance metrics

### Application Logs

Structured logging with configurable levels:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 🔒 Security

### Production Checklist

- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/TLS
- [ ] Add API Gateway with authentication
- [ ] Implement rate limiting
- [ ] Configure CORS appropriately
- [ ] Use Docker security best practices
- [ ] Enable container scanning
- [ ] Set up monitoring and alerts

## 🎯 Success Criteria

- ✅ **Accuracy**: ≥ 90% of prompts parsed correctly
- ✅ **Performance**: API response < 2s average
- ✅ **Coverage**: All supported fields/operators validated
- ✅ **Observability**: 100% of requests traced in LangSmith

## 🐛 Troubleshooting

### Common Issues

**Issue: `OPENAI_API_KEY not found`**
```bash
# Make sure .env file exists and contains your API key
cp .env.example .env
# Edit .env and add your key
```

**Issue: Import errors**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: Port already in use**
```bash
# Change the port in .env
API_PORT=8001
# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## 📈 Performance Optimization

- **Caching**: Consider caching common prompts
- **Batching**: Implement batch processing endpoint
- **Scaling**: Use horizontal scaling with load balancer
- **Model**: Evaluate GPT-3.5 for faster/cheaper responses
- **Rate Limiting**: Implement to prevent abuse

## 🛠️ Make Commands

```bash
make help          # Show all available commands
make init          # Initial setup (env + install)
make install       # Install dependencies
make run           # Run locally
make test          # Run tests
make test-cov      # Run tests with coverage
make docker-build  # Build Docker image
make docker-compose # Run with Docker Compose
make evaluate      # Evaluate accuracy
make clean         # Clean generated files
make lint          # Run linters
make format        # Format code
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the amazing LLM orchestration framework
- **FastAPI** for the modern Python web framework
- **OpenAI** for GPT-4 language model
- **LangSmith** for observability tools

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review [API specification](docs/api_spec.md)

---

**Built with ❤️ using LangGraph, LangChain, and FastAPI**
