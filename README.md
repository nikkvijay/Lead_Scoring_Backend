# Lead Scoring Backend API

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-brightgreen)](https://lead-scoring-backend-b0hv.onrender.com)

> AI-powered lead scoring system that combines rule-based logic with artificial intelligence to qualify sales prospects and predict buying intent.

## 🌐 Live Demo

**API Base URL:** https://lead-scoring-backend-b0hv.onrender.com

**Interactive Documentation:** https://lead-scoring-backend-b0hv.onrender.com/docs

**Health Check:** https://lead-scoring-backend-b0hv.onrender.com/health

## 🚀 Features

- **Hybrid Scoring Engine**: Combines rule-based logic (50%) with AI analysis (50%)
- **Multi-Provider AI**: Support for Google Gemini (free) and OpenAI (paid) with automatic fallback
- **CSV Bulk Processing**: Upload and score hundreds of leads simultaneously
- **RESTful API Design**: Clean, documented endpoints with automatic OpenAPI documentation
- **Cost Optimization**: Smart provider selection and usage tracking
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## 📋 API Endpoints

### Core Functionality
- `POST /api/v1/offer` - Store product/offer information
- `POST /api/v1/leads/upload` - Upload leads via CSV file
- `POST /api/v1/score` - Execute scoring pipeline
- `GET /api/v1/results` - Retrieve scoring results
- `GET /api/v1/results/export` - Export results as CSV (bonus)
- `GET /api/v1/usage-stats` - View AI usage statistics (bonus)

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- AI Provider API Keys (at least one):
  - Google Gemini API Key (free tier)
  - OpenAI API Key (paid)

### Local Development

1. **Clone and setup virtual environment**
   ```bash
   git clone https://github.com/nikkvijay/Lead_Scoring_Backend
   cd Lead_Scoring_Backend

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📚 API Usage Examples

### 1. Store Offer

**Live Demo:**
```bash
curl -X POST "https://lead-scoring-backend-b0hv.onrender.com/api/v1/offer" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 automated outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS companies", "Mid-market technology"]
  }'
```

**Local Development:**
```bash
curl -X POST "http://localhost:8000/api/v1/offer" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 automated outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS companies", "Mid-market technology"]
  }'
```

### 2. Upload Leads CSV

Create `leads.csv`:
```csv
name,role,company,industry,location,linkedin_bio
Ava Patel,Head of Growth,FlowMetrics,software,San Francisco,Leading growth at B2B SaaS startup
```

**Live Demo:**
```bash
curl -X POST "https://lead-scoring-backend-b0hv.onrender.com/api/v1/leads/upload" -F "file=@leads.csv"
```

**Local Development:**
```bash
curl -X POST "http://localhost:8000/api/v1/leads/upload" -F "file=@leads.csv"
```

### 3. Execute Scoring

**Live Demo:**
```bash
curl -X POST "https://lead-scoring-backend-b0hv.onrender.com/api/v1/score"
```

**Local Development:**
```bash
curl -X POST "http://localhost:8000/api/v1/score"
```

### 4. Get Results

**Live Demo:**
```bash
curl "https://lead-scoring-backend-b0hv.onrender.com/api/v1/results"
```

**Local Development:**
```bash
curl "http://localhost:8000/api/v1/results"
```

## 🤖 AI Provider Strategy

### Cost Optimization

- **Primary**: Google Gemini (free tier, 15 requests/minute)
- **Fallback**: OpenAI GPT-4o-mini (paid, ~$0.0001 per request)
- **Smart Switching**: Automatically falls back if primary fails or hits limits

### Rule Logic

- **Role**: Decision maker (20pts), Influencer (10pts), Other (0pts)
- **Industry**: Exact match (20pts), Related (10pts), No match (0pts)
- **Completeness**: All fields present (10pts)
- **AI**: High=50pts, Medium=30pts, Low=10pts

### AI Prompt Template

```
Analyze buying intent: High/Medium/Low

Product: {product_name}
Use cases: {use_cases_limited}

Prospect: {name}, {role} at {company}
Industry: {industry}
Bio: {bio_truncated}

JSON only: {"intent": "High|Medium|Low", "reasoning": "Brief explanation"}
```

## 🧪 Testing

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### 🐳 Docker Deployment (Recommended)

#### Quick Start with Docker Compose
```bash
# 1. Clone repository
git clone https://github.com/nikkvijay/Lead_Scoring_Backend
cd Lead_Scoring_Backend

# 2. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Run with Docker Compose
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop containers
docker-compose down
```

#### Manual Docker Build
```bash
# Build image
docker build -t lead-scoring-backend .

# Run container
docker run -d \
  --name lead-scoring-api \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key_here \
  -e OPENAI_API_KEY=your_key_here \
  lead-scoring-backend

# View logs
docker logs -f lead-scoring-api
```

#### Production with Nginx (Optional)
```bash
# Run with nginx reverse proxy
docker-compose --profile production up -d
```

### 🌐 Cloud Deployment

#### Deploy to Render
1. **Setup Repository**
   - Connect GitHub repository to Render
   - Set environment variables:
     - `GEMINI_API_KEY`
     - `OPENAI_API_KEY` (optional)

2. **Build Configuration**
   ```bash
   # Build Command:
   python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

   # Start Command:
   source venv/bin/activate && gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

#### Deploy to Railway
```bash
# Build Command:
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Start Command:
source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Deploy to AWS/GCP/Azure
Use the provided `Dockerfile` with your preferred container service:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

## 📁 Project Structure

```
Lead_Scoring_Backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/                # Configuration & exceptions
│   │   ├── config.py        # Settings management
│   │   ├── constants.py     # Business logic constants
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/              # Pydantic data models
│   │   ├── lead.py          # Lead and scoring models
│   │   └── offer.py         # Offer/product models
│   ├── routers/             # API endpoints
│   │   ├── offers.py        # Offer management
│   │   ├── leads.py         # Lead upload & management
│   │   └── scoring.py       # Scoring & results
│   ├── services/            # Business logic
│   │   ├── ai_service.py    # AI provider integration
│   │   ├── scoring_engine.py # Hybrid scoring logic
│   │   ├── csv_processor.py # CSV handling
│   │   └── storage_service.py # In-memory storage
│   └── utils/               # Utility functions
├── tests/
│   └── unit/                # Unit tests
│       └── test_ai_fallback.py
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file with:

```env
# AI Provider Keys (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# AI Configuration
AI_PRIMARY_PROVIDER=gemini
AI_FALLBACK_ENABLED=true
AI_MAX_RETRIES=2
AI_TIMEOUT=15

# Business Logic
MAX_LEADS_PER_UPLOAD=1000
MAX_FILE_SIZE_MB=10

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

## 🔧 Troubleshooting

### Common Issues

1. **AI Service Errors**
   - Verify API keys are set correctly
   - Check provider quotas and limits
   - Review logs for specific error messages

2. **CSV Upload Issues**
   - Ensure CSV has required columns: `name`, `role`, `company`, `industry`, `location`, `linkedin_bio`
   - Check file size limits (default: 10MB)
   - Verify CSV encoding (UTF-8 recommended)

3. **Virtual Environment Issues**
   - Ensure Python 3.11+ is installed
   - Recreate virtual environment if dependencies conflict
   - Use `pip list` to verify installed packages

### Development Tips

- Use `/docs` endpoint for interactive API documentation
- Monitor `/api/v1/usage-stats` for AI cost tracking
- Check logs for detailed error information
- Use `/health` endpoint for service monitoring

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review API documentation at `/docs` endpoint