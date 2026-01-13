# Getting Started Guide - CV Matching RAG System

## Quick Setup Instructions

### Step 1: Clone/Navigate to Project
```bash
cd c:/Users/Joy/Desktop/MyProjects/Prototypes/recruitment-dash1
```

### Step 2: Configure Environment Variables

**For Docker:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

**For Local Development:**

Backend:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

Frontend:
```bash
cd frontend
cp .env.example .env
# Edit .env with backend URL
```

### Step 3: Add Your API Keys

You need to get API keys from:

1. **OpenAI** (https://platform.openai.com/api-keys)
   - Add to: `OPENAI_API_KEY`

2. **Pinecone** (https://www.pinecone.io/)
   - Add to: `PINECONE_API_KEY`
   - Create index: `cv-matching-index`
   - Add: `PINECONE_ENVIRONMENT`

3. **Langfuse** (https://cloud.langfuse.com/) - Optional
   - Add: `LANGFUSE_PUBLIC_KEY`
   - Add: `LANGFUSE_SECRET_KEY`

4. **Claude** (Optional) - https://console.anthropic.com/
   - Add to: `CLAUDE_API_KEY`

5. **Grok** (Optional) - https://api.x.ai/
   - Add to: `GROK_API_KEY`

### Step 4: Run with Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access the application:
- **Frontend**: http://localhost:3301
- **Backend API**: http://localhost:8801
- **API Docs**: http://localhost:8801/docs

### Step 5: Run Locally (Alternative)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8801
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. **Upload CVs** - Navigate to "Upload CVs" tab and select CV files
2. **Enter Job Description** - Go to "Match" tab and enter:
   - Job Title
   - Job Description
   - Required Skills (optional)
3. **View Results** - Check "Results" tab for ranked matches

## Architecture Overview

### Backend (Port 8801)
- FastAPI REST API
- LangGraph RAG orchestration
- Pinecone vector store integration
- Multi-LLM support (OpenAI, Claude, Grok)
- Langfuse observability

### Frontend (Port 3301)
- Streamlit web interface
- CV upload management
- Job description input
- Results visualization
- Real-time feedback

### Data Flow
```
CVs (PDF/DOCX/TXT)
    ↓
Embedding Service (SentenceTransformers)
    ↓
Pinecone Vector Store
    ↓
Job Description
    ↓
LangGraph Orchestration Pipeline
    ├─ Embed JD
    ├─ Retrieve Similar CVs
    ├─ Analyze Content
    ├─ LLM Scoring
    └─ Format Results
    ↓
Streamlit Dashboard
```

## Key Features Implemented

✅ Streamlit Frontend (Port 3301)
✅ FastAPI Backend (Port 8801)
✅ LangGraph Orchestration
✅ Pinecone Vector Store
✅ Multi-LLM Support
✅ Langfuse Observability
✅ Docker & Docker Compose
✅ RESTful API Endpoints
✅ CV Management
✅ Job Matching

## Project Files

**Backend:**
- `backend/app/core/config.py` - Configuration
- `backend/app/core/rag_orchestrator.py` - LangGraph workflow
- `backend/app/services/embedding_service.py` - Embeddings
- `backend/app/services/vector_store_service.py` - Pinecone
- `backend/app/services/llm_service.py` - LLM integration
- `backend/app/services/observability_service.py` - Langfuse
- `backend/app/routes/cv_routes.py` - CV endpoints
- `backend/app/routes/matching_routes.py` - Matching endpoints
- `backend/app/models/schemas.py` - Data models

**Frontend:**
- `frontend/app.py` - Main Streamlit app
- `frontend/services/api_client.py` - Backend API client
- `frontend/.streamlit/config.toml` - Streamlit config

**Docker:**
- `Dockerfile.backend` - Backend container
- `Dockerfile.frontend` - Frontend container
- `docker-compose.yml` - Orchestration

## Environment Variables Reference

```
# Required
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...

# Optional
CLAUDE_API_KEY=sk-ant-...
GROK_API_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...

# URLs
BACKEND_URL=http://localhost:8801
FRONTEND_URL=http://localhost:3301

# Settings
LLM_PROVIDER=openai
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=cv-matching-index
```

## Troubleshooting

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :3301
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :3301
kill -9 <PID>
```

**Docker not starting:**
```bash
# Check Docker status
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

**API connection issues:**
```bash
# Check backend health
curl http://localhost:8801/health

# Check logs
docker-compose logs backend
```

## Next Steps

1. Set up your API keys in `.env`
2. Run `docker-compose up` to start all services
3. Open http://localhost:3301 in your browser
4. Upload some sample CVs
5. Create a job description and match!

## Support

For detailed information, see:
- README.md - Full documentation
- API Docs: http://localhost:8801/docs (when running)
- Code comments in each module

---

**Ready to get started?** Follow the setup steps above!
