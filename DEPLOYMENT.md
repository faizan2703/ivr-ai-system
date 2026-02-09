# IVR AI Agent System - Deployment & Checklist

## Pre-Deployment Checklist

### Development Setup ✓
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`
- [ ] OpenAI API key obtained and added to `.env`

### Code Quality
- [ ] No syntax errors
- [ ] Input validation working
- [ ] Error handling implemented
- [ ] Logs are being captured
- [ ] Documentation complete

### Testing
- [ ] API health check passing
- [ ] Call initiation working
- [ ] Message processing working
- [ ] Knowledge base search working
- [ ] File upload working
- [ ] Call termination working

### Knowledge Base
- [ ] Sample documents added
- [ ] Categories defined
- [ ] Search testing successful
- [ ] Relevance scoring working
- [ ] Document updates working

### Frontend
- [ ] UI loads without errors
- [ ] All buttons functional
- [ ] Forms validate properly
- [ ] Chat interface working
- [ ] Real-time updates working
- [ ] Responsive design checked

### Backend Configuration
- [ ] Debug mode set appropriately
- [ ] CORS configured
- [ ] Request timeout set
- [ ] Error logging enabled
- [ ] Rate limiting considered

## Local Development Setup

```bash
# 1. Clone/Setup project
cd ivr-ai-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 5. Run backend
cd backend
python main.py

# 6. In another terminal, run frontend
cd frontend
python -m http.server 8080

# 7. Open browser
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

## Docker Deployment

### Build Docker Image
```bash
# Build image
docker build -t ivr-system:latest .

# Verify build
docker images | grep ivr-system
```

### Run Single Container
```bash
# Run with environment variable
docker run -d \
  -p 8000:8000 \
  -p 8080:8080 \
  -e "OPENAI_API_KEY=sk-your-key" \
  -v $(pwd)/data:/app/data \
  --name ivr-system \
  ivr-system:latest

# Check logs
docker logs ivr-system

# Stop container
docker stop ivr-system
docker rm ivr-system
```

### Docker Compose (Recommended)
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## Cloud Deployment

### AWS Deployment (ECS)
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name ivr-system

# 2. Build and push image
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag ivr-system:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ivr-system:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ivr-system:latest

# 3. Create ECS cluster and task definition
# (See AWS documentation)

# 4. Deploy to ECS
aws ecs create-service --cluster ivr-cluster --service-name ivr-service ...
```

### Google Cloud Run
```bash
# 1. Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/ivr-system

# 2. Deploy
gcloud run deploy ivr-system \
  --image gcr.io/PROJECT_ID/ivr-system \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=sk-your-key
```

### Azure Container Instances
```bash
# 1. Create container registry
az acr create --resource-group myGroup --name ivrregistry --sku Basic

# 2. Build and push
az acr build --registry ivrregistry --image ivr-system:latest .

# 3. Deploy
az container create \
  --resource-group myGroup \
  --name ivr-system \
  --image ivrregistry.azurecr.io/ivr-system:latest
```

## Production Configuration

### Environment Variables
```bash
# Server
DEBUG=False
HOST=0.0.0.0
PORT=8000

# API Keys (use secure vaults)
OPENAI_API_KEY=${SECRET_OPENAI_KEY}

# Database
VECTOR_DB_PATH=/data/chroma
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional: Twilio for phone support
TWILIO_ACCOUNT_SID=${SECRET_TWILIO_SID}
TWILIO_AUTH_TOKEN=${SECRET_TWILIO_TOKEN}
TWILIO_PHONE_NUMBER=+1234567890

# Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_TOP_K=3
MAX_RETRIES=3
CONVERSATION_TIMEOUT=300
```

### Security Hardening

#### 1. HTTPS/TLS
```nginx
# Nginx reverse proxy configuration
server {
    listen 443 ssl http2;
    server_name api.ivr-system.com;
    
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. Authentication
```python
# Add JWT authentication
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.post("/api/v1/calls/initiate")
async def initiate_call(request: CallRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify JWT token
    payload = verify_token(credentials.credentials)
    # Process request
```

#### 3. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/calls/initiate")
@limiter.limit("50/minute")
async def initiate_call(request: CallRequest):
    # Rate limited to 50 requests per minute
```

#### 4. CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specific methods
    allow_headers=["Authorization", "Content-Type"],  # Specific headers
)
```

### Database Persistence
```python
# Persistent Chroma database on cloud storage
import os
from chromadb.config import Settings

chroma_settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/data/chroma",
    anonymized_telemetry=False,
)
```

### Logging & Monitoring
```python
import logging
from pythonjsonlogger import jsonlogger

# JSON structured logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"Request completed", extra={
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration": duration
    })
    return response
```

## Performance Tuning

### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_document_by_id(doc_id: str):
    # Cache recent lookups
    return rag_service.get_document(doc_id)
```

### 2. Async Processing
```python
from celery import Celery
from celery.backends.redis import RedisBackend

app = Celery('ivr_system', broker='redis://localhost:6379')

@app.task
def process_document_async(doc_id: str):
    # Process document in background
    rag_service.update_embeddings(doc_id)
```

### 3. Connection Pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

## Monitoring & Alerts

### Key Metrics
```python
from prometheus_client import Counter, Histogram

# Track API calls
api_calls = Counter('ivr_api_calls_total', 'Total API calls')
api_latency = Histogram('ivr_api_latency_seconds', 'API latency')

# Track calls
active_calls = Gauge('ivr_active_calls', 'Active calls')

# Track errors
api_errors = Counter('ivr_api_errors_total', 'Total errors')
```

### Health Checks
```python
@app.get("/health")
async def health():
    checks = {
        "api": "ok",
        "rag_db": await check_vector_db(),
        "llm": await check_openai(),
        "redis": await check_redis()
    }
    status = "healthy" if all(checks.values()) == [True] * len(checks) else "unhealthy"
    return {"status": status, "checks": checks}
```

## Backup & Recovery

### Knowledge Base Backup
```bash
# Backup Chroma DB
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz ./data/chroma

# Restore
tar -xzf chroma_backup_20240209.tar.gz -C ./data
```

### Database Replication
```bash
# Setup PostgreSQL replication for call logs
# Primary → Replica synchronization
```

## Scaling Strategies

### Horizontal Scaling
```
Load Balancer
    ↓
├─→ IVR Instance 1
├─→ IVR Instance 2
├─→ IVR Instance 3
    ↓
Shared Redis (sessions)
Shared Chroma DB (vector store)
```

### Vertical Scaling
- Increase CPU/RAM for single instance
- Use GPU for faster embeddings
- Optimize LLM inference

## Deployment Commands

```bash
# Quick deployment checklist
make install              # Install dependencies
make setup-env           # Setup environment
make test-health         # Verify backend
make docker-build        # Build image
make docker-compose      # Deploy locally

# Production deployment
docker build -t ivr-system:prod .
docker push registry/ivr-system:prod
kubectl apply -f k8s/deployment.yaml
```

## Post-Deployment

### Verification
- [ ] All endpoints responding
- [ ] Health check passing
- [ ] Knowledge base loaded
- [ ] File uploads working
- [ ] WebSocket connections working

### Monitoring
- [ ] Logs being collected
- [ ] Metrics being tracked
- [ ] Alerts configured
- [ ] Error tracking set up

### Optimization
- [ ] Cache performance tuning
- [ ] Database performance tuning
- [ ] API response time tuning
- [ ] Resource usage optimization

## Rollback Procedures

```bash
# If deployment fails
docker-compose down

# Switch to previous version
docker run -e OPENAI_API_KEY=$KEY ivr-system:previous

# Restore database from backup
tar -xzf chroma_backup_previous.tar.gz
```

## Support & Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version: `python --version`
- Check dependencies: `pip list`
- Check .env: `echo $OPENAI_API_KEY`

**API returning errors**
- Check logs: `docker logs ivr-system`
- Check connectivity: `curl http://localhost:8000/health`

**High latency**
- Monitor: `docker stats`
- Check embeddings cache
- Optimize chunk size

**Out of memory**
- Reduce batch size
- Increase timeout
- Enable garbage collection

---

**Deployment Status**: Ready for production ✓
