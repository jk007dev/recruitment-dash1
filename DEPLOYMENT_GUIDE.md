# 🚀 CV Matching RAG System - Deployment & Operations Guide

## System Overview

A production-ready, intelligent CV matching system using:
- **Frontend**: Streamlit (Port 3301)
- **Backend**: FastAPI (Port 8801)
- **Orchestration**: LangGraph
- **Vector DB**: Pinecone
- **LLMs**: OpenAI, Claude, Grok
- **Observability**: Langfuse
- **Containerization**: Docker & Docker Compose

## Prerequisites

### System Requirements
- Docker & Docker Desktop (latest version)
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- Internet connection (for API calls)

### API Keys Required

1. **OpenAI** (https://platform.openai.com/api-keys)
   - Minimum: gpt-4-turbo-preview
   - Cost: ~$0.03 per 1K tokens input, ~$0.06 per 1K output
   - Sign up for credits

2. **Pinecone** (https://www.pinecone.io)
   - Create serverless index
   - Free tier: 1M vectors + 1M requests/month
   - Region: us-east-1-aws

3. **Langfuse** (https://cloud.langfuse.com) - Optional
   - Free tier available
   - For observability and monitoring

4. **Claude or Grok** (Optional)
   - Alternative to OpenAI
   - Anthropic: https://console.anthropic.com/
   - xAI: https://api.x.ai/

## Installation & Setup

### Step 1: Clone/Navigate to Project
```bash
cd c:/Users/Joy/Desktop/MyProjects/Prototypes/recruitment-dash1
```

### Step 2: Environment Configuration

**Global Configuration:**
```bash
cp .env.example .env
```

Edit `.env` file with your API keys:
```
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=cv-matching-index
LANGFUSE_PUBLIC_KEY=your-key
LANGFUSE_SECRET_KEY=your-secret
```

### Step 3: Verify Docker Installation
```bash
docker --version
docker-compose --version
docker ps  # Should show no errors
```

### Step 4: Build Docker Images
```bash
# From project root
docker-compose build

# With no cache (if updating)
docker-compose build --no-cache
```

### Step 5: Start Services
```bash
# Start all services in background
docker-compose up -d

# Wait 30 seconds for services to initialize
timeout 30

# Verify all services are running
docker-compose ps
```

### Step 6: Verify Deployment
```bash
# Check backend health
curl http://localhost:8801/health

# Check frontend is running
curl http://localhost:3301 2>/dev/null | head -20

# View backend API docs
# Open browser: http://localhost:8801/docs
```

## Usage Guide

### Access the Application

1. **Open Frontend**: http://localhost:3301
2. **API Documentation**: http://localhost:8801/docs
3. **Backend Health**: http://localhost:8801/health

### Upload CVs

**Via Web Interface:**
1. Go to "Upload CVs" tab
2. Click "Browse" and select CV files
3. Supported formats: PDF, DOCX, TXT
4. Click "Upload Selected" button
5. Wait for confirmation

**API Command:**
```bash
curl -X POST "http://localhost:8801/api/cv/upload" \
  -F "file=@resume.pdf" \
  -F "cv_id=john_doe_001"
```

### Create Matching Job

**Via Web Interface:**
1. Go to "Match" tab
2. Enter Job Title (required)
3. Enter Job Description (required)
4. Enter Required Skills (optional)
5. Select LLM Provider
6. Set "Number of Top Matches"
7. Click "Find Matching CVs"

**API Command:**
```bash
curl -X POST "http://localhost:8801/api/matching/match" \
  -H "Content-Type: application/json" \
  -d '{
    "jd": {
      "job_title": "Senior Python Developer",
      "job_description": "We seek...",
      "required_skills": ["Python", "FastAPI"]
    },
    "cv_ids": ["cv_001", "cv_002", "cv_003"],
    "llm_provider": "openai",
    "top_k": 5
  }'
```

### View Results

1. Go to "Results" tab
2. See ranked CVs by match score
3. Expand each result for details:
   - Match score percentage
   - Experience alignment
   - Matched skills
   - LLM reasoning
   - Overall assessment

## Monitoring & Observability

### View Logs

**All Services:**
```bash
docker-compose logs
```

**Specific Service:**
```bash
docker-compose logs backend    # Just backend
docker-compose logs frontend   # Just frontend
```

**Real-time Logs:**
```bash
docker-compose logs -f --tail=50
```

### Health Checks

**Backend:**
```bash
curl http://localhost:8801/health
# Response: {"status":"healthy","service":"CV Matching RAG API",...}
```

**System:**
```bash
docker-compose ps
# Shows status of all containers
```

**Container Details:**
```bash
docker-compose exec backend sh -c "curl http://localhost:8801/health"
```

### Langfuse Observability

1. Go to https://cloud.langfuse.com
2. Login with your credentials
3. View:
   - CV matching events
   - Embedding generations
   - LLM calls
   - Performance metrics
   - Error logs

## Maintenance & Operations

### Regular Tasks

**Daily:**
- Monitor logs for errors
- Check Langfuse for anomalies
- Verify API usage costs

**Weekly:**
- Review matching results
- Check disk space usage
- Monitor API quotas

**Monthly:**
- Update dependencies
- Review performance metrics
- Backup important data

### Scaling

**Increase Memory:**
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
```

**Increase Workers:**
Backend: Modify uvicorn command in Dockerfile
Frontend: Streamlit auto-scales

### Performance Optimization

1. **Reduce embedding model size** if memory constrained
2. **Increase Pinecone `max_cv_results`** for wider search
3. **Batch process CVs** for multiple uploads
4. **Cache embeddings** for repeated searches
5. **Use asynchronous processing** for large batches

## Troubleshooting Guide

### Issue: Port Already in Use

**Solution 1 - Use Different Port:**
```bash
# Edit docker-compose.yml
# Change "3301:3301" to "3302:3301"
docker-compose down
docker-compose up -d
```

**Solution 2 - Kill Process:**
```bash
# Windows PowerShell
netstat -ano | findstr :3301
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :3301
kill -9 <PID>
```

### Issue: Pinecone Connection Error

**Check:**
```bash
# Verify API key is correct
echo $PINECONE_API_KEY

# Check index exists in Pinecone dashboard
# https://app.pinecone.io
```

**Solution:**
```bash
# Recreate with correct key
docker-compose down
# Update .env with correct PINECONE_API_KEY
docker-compose up -d
```

### Issue: OpenAI API Error

**Check:**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Common Fixes:**
- Ensure key starts with `sk-`
- Check account has credits
- Verify API limits not exceeded

### Issue: Frontend Can't Connect to Backend

**Check:**
```bash
# From frontend container
docker-compose exec frontend curl http://backend:8801/health

# Check docker network
docker-compose exec backend ifconfig
docker-compose exec frontend ifconfig
```

**Solution:**
```bash
# Restart services
docker-compose down
docker-compose up -d
```

### Issue: Memory Issues

**Check:**
```bash
docker stats

# Should show memory usage < available RAM
```

**Solution:**
1. Reduce batch size for CV processing
2. Use lighter embedding model
3. Increase Docker memory allocation
4. Delete old containers: `docker-compose down -v`

### Issue: Slow Performance

**Check:**
```bash
docker-compose logs -f --tail=100
# Look for slow API calls or database queries
```

**Solutions:**
1. Check Langfuse for bottlenecks
2. Monitor API quota usage
3. Optimize Pinecone index
4. Reduce number of CVs in search
5. Use faster LLM model (gpt-4 → gpt-3.5-turbo)

## Updating & Upgrades

### Update Python Dependencies

```bash
# Pull latest images
docker-compose build --no-cache

# Restart with new images
docker-compose down
docker-compose up -d
```

### Update to New Version

```bash
# Backup current .env
cp .env .env.backup

# Pull latest code
git pull  # if using git

# Rebuild
docker-compose build --no-cache

# Update
docker-compose down
docker-compose up -d
```

### Rollback

```bash
# Restore from backup
docker-compose down
cp .env.backup .env
docker-compose up -d
```

## Backup & Recovery

### Backup Configuration

```bash
# Backup .env files
cp .env .env.backup.$(date +%Y%m%d)
cp backend/.env backend/.env.backup.$(date +%Y%m%d)
cp frontend/.env frontend/.env.backup.$(date +%Y%m%d)

# Store in safe location
```

### Backup Data

CVs are stored in Pinecone cloud, so no local backup needed.
However, keep records of:
- Matching results
- Job descriptions used
- API usage logs

### Recovery Steps

```bash
# From .env backup
cp .env.backup .env

# Restart services
docker-compose down
docker-compose up -d

# Verify
curl http://localhost:8801/health
```

## Security Best Practices

1. **API Keys**
   - Store in .env (never in code)
   - Rotate keys quarterly
   - Use separate keys for dev/prod

2. **Network**
   - Use Docker network isolation
   - Firewall ports 3301 and 8801
   - Use HTTPS in production (add reverse proxy)

3. **Data**
   - CVs stored securely in Pinecone
   - Enable audit logging
   - Regular security updates

4. **Access**
   - Restrict backend to internal network
   - Add authentication in production
   - Monitor access logs

## Cost Optimization

### API Usage Costs

**OpenAI:**
- ~$0.03 per 1K input tokens
- ~$0.06 per 1K output tokens
- Estimate: $0.10-0.50 per CV match

**Pinecone:**
- Free tier: $0
- Paid: $0.25 per 1M vectors per month
- Free tier covers 1M vectors

**Langfuse:**
- Free: $0
- Pro: $9/month

### Cost Reduction

1. Use gpt-3.5-turbo instead of gpt-4
2. Batch process CVs
3. Cache embeddings
4. Limit context size
5. Use Claude for non-critical tasks

## Production Deployment

### Pre-Production Checklist

- [ ] All environment variables set
- [ ] API keys verified
- [ ] Docker images built
- [ ] Containers starting successfully
- [ ] All endpoints responding
- [ ] Frontend loading
- [ ] Basic CV upload test
- [ ] Matching test
- [ ] Results display correct
- [ ] Logs show no errors

### Production Setup

```bash
# Use same docker-compose with:
# - Fixed image versions (not latest)
# - Resource limits
# - Restart policies
# - Health checks enabled

# Example
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoring in Production

1. Set up log aggregation (ELK, Datadog)
2. Configure alerts for errors
3. Monitor API rate limits
4. Track costs
5. Regular security audits

## Support & Troubleshooting

### Get Help

1. Check logs: `docker-compose logs -f`
2. Review documentation files
3. Check API docs: http://localhost:8801/docs
4. Test components individually
5. Check GitHub issues/discussions

### Report Issues

Include:
- Docker version
- API error messages
- Logs from `docker-compose logs`
- Steps to reproduce
- Expected vs actual behavior

### Common Commands Cheat Sheet

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose build

# Remove all data
docker-compose down -v

# Check status
docker-compose ps

# Execute command
docker-compose exec backend bash
docker-compose exec frontend bash

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Performance Metrics

### Expected Response Times

| Operation | Time |
|-----------|------|
| CV Upload | 1-2 seconds |
| Embedding Generation | < 500ms |
| Pinecone Query | 50-200ms |
| LLM Analysis | 2-5 seconds |
| Total Match | 5-10 seconds |

### Resource Usage

| Component | CPU | Memory | Disk |
|-----------|-----|--------|------|
| Backend | 0.5-1 CPU | 500-800MB | 200MB |
| Frontend | 0.2 CPU | 300-500MB | 300MB |
| Total | ~1.5 CPU | ~1.3GB | ~500MB |

## Version Information

- **Project Version**: 1.0.0
- **Python**: 3.11+
- **FastAPI**: 0.104.1
- **Streamlit**: 1.28.1
- **LangGraph**: 0.0.32
- **Pinecone**: 3.0.0
- **Docker**: Latest

---

**Last Updated**: January 12, 2026
**Status**: Production Ready ✅

For detailed documentation, see:
- README.md
- GETTING_STARTED.md
- FILE_STRUCTURE.md
- CHECKLIST.md
