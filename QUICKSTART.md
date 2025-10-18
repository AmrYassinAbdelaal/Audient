# Quick Start Guide - Audient

Get Audient up and running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step 1: Setup

```bash
# Navigate to the project
cd Audient

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

## Step 2: Configure

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Optional - Add LangSmith for observability:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=audient
```

## Step 3: Run

```bash
# Start the server
python -m uvicorn app.main:app --reload

# Or use the convenience script
./scripts/run_local.sh

# Or use Make
make run
```

The server will start at: **http://localhost:8000**

## Step 4: Test

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/parse_prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find female customers in Riyadh with more than 1000 sales"}'
```

### Using the Interactive Docs

Open your browser and go to: **http://localhost:8000/docs**

Try these example prompts:

**English:**
- "Find female customers"
- "Customers with more than 10 orders"
- "Stores rated between 3 and 5 stars"
- "Find customers who joined after Jan 2023 with more than 5 orders"

**Arabic:**
- "اعثر على العملاء الإناث"
- "العملاء الذين لديهم أكثر من 10 طلبات"
- "المتاجر التي تقييمها بين 3 و 5 نجوم"

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/parse_prompt",
    json={"prompt": "Find female customers in Riyadh"}
)

print(response.json())
```

## Step 5: Run Tests

```bash
# Run all tests
pytest app/tests/

# Run with coverage
pytest app/tests/ --cov=app --cov-report=html

# Or use Make
make test
make test-cov
```

## Common Issues

### Port Already in Use

```bash
# Change port in .env
API_PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### Missing API Key

```bash
# Make sure .env file exists and has your key
cat .env | grep OPENAI_API_KEY
```

### Import Errors

```bash
# Make sure you're in the virtual environment
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

- 📖 Read the [full documentation](README.md)
- 🧪 Review the [testing plan](docs/testing_plan.md)
- 🔧 Check the [API specification](docs/api_spec.md)
- 🐳 Try [Docker deployment](#docker)
- ☁️ Deploy to [cloud](#cloud-deployment)

## Docker (Optional)

```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up

# Or use Make
make docker-compose

# Or manually
docker build -f docker/Dockerfile -t audient .
docker run -p 8000:8000 --env-file .env audient
```

## Cloud Deployment (Optional)

### AWS

```bash
./scripts/deploy_aws.sh
```

### GCP

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/audient
gcloud run deploy --image gcr.io/PROJECT_ID/audient
```

## Evaluation

Evaluate the model accuracy:

```bash
python scripts/evaluate_accuracy.py --language both --output report.json
# or
make evaluate
```

## Need Help?

- Check the [troubleshooting section](README.md#troubleshooting)
- Review the [API docs](http://localhost:8000/docs)
- Open an issue on GitHub

---

**Happy filtering! 🎯**
