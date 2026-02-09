# IVR AI Agent System - Comprehensive Guide

## Overview

**IVR AI Agent System** is a production-ready Interactive Voice Response (IVR) solution powered by generative AI and Retrieval Augmented Generation (RAG). It features an intelligent agent that can handle customer interactions, access a knowledge base for accurate responses, and intelligently route calls.

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **RAG System**: LangChain + Chromadb for semantic search
- **AI Agent**: OpenAI GPT-4 with context awareness
- **Service Layer**: Modular services for calls, conversations, and knowledge base

### Frontend (Modern Web UI)
- **Technology**: HTML5, CSS3, JavaScript
- **Design**: Responsive modern UI with gradient themes
- **Features**: Real-time chat, call management, knowledge base search, file upload

## Features

✨ **Core Features**
- 🤖 AI-powered conversational IVR agent
- 🔍 RAG-based knowledge base system
- 📞 Call initiation and management
- 💬 Real-time conversation handling
- 📚 Document management and search
- 📊 Dashboard with call analytics
- 🎯 Intent detection and call routing
- 🔄 WebSocket support for real-time updates

## Project Structure

```
ivr-ai-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py           # Configuration settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py          # Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py      # RAG & knowledge base
│   │   │   ├── agent_service.py    # AI agent logic
│   │   │   └── call_manager.py     # Call management
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py           # Health checks
│   │       ├── calls.py            # Call management endpoints
│   │       ├── conversations.py    # Message handling
│   │       └── knowledge.py        # Knowledge base endpoints
│   └── main.py                     # FastAPI application
├── frontend/
│   ├── index.html                  # Main UI
│   ├── styles.css                  # Stylesheet
│   └── script.js                   # JavaScript logic
├── knowledge_base/                 # Knowledge base documents store
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .env                           # Environment variables
└── README.md                       # This file
```

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- pip or conda
- OpenAI API key (from https://platform.openai.com)

### 2. Backend Setup

```bash
# Navigate to project directory
cd ivr-ai-system

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Start the Backend

```bash
# From the backend directory or project root
python backend/main.py

# Or with uvicorn directly
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### 4. Frontend Setup

Option A: Open directly
```bash
# Simply open frontend/index.html in your browser
# Or serve with Python
cd frontend
python -m http.server 8080
# Visit http://localhost:8080
```

Option B: Using a web server
```bash
# Using Node.js http-server
npx http-server frontend

# Or any other static server
```

## Usage Guide

### 1. Initialize a Call

```
1. Navigate to "Make Call" section
2. Enter customer details:
   - Name
   - Phone number
   - Issue/Topic
3. Click "Initiate Call"
```

### 2. Manage Conversation

```
1. Type your message in the chat box
2. Press Enter or click Send
3. Agent responds automatically
4. View intent and confidence scores
5. Transfer to human if needed
6. End call when done
```

### 3. Knowledge Base Management

```
1. Go to "Knowledge Base" section
2. Add Document:
   - Enter title, category, content
   - Click "Add Document"
3. Upload Files:
   - Click upload area
   - Select .txt, .pdf, or .doc files
4. Search:
   - Enter query
   - View top 5 results
   - Results show relevance scores
```

### 4. Monitor Dashboard

```
- Active Calls: Real-time call count
- Total Calls: Historical statistics
- Knowledge Docs: Total documents in KB
- System Status: Backend health
- Active Calls List: Details of ongoing calls
```

## API Endpoints

### Health & Status
- `GET /api/v1/health` - System health check
- `GET /api/v1/status` - System status

### Call Management
- `POST /api/v1/calls/initiate` - Start new call
- `GET /api/v1/calls/status/{call_id}` - Get call status
- `POST /api/v1/calls/end/{call_id}` - End call
- `GET /api/v1/calls/active` - Get active calls

### Conversations
- `POST /api/v1/conversations/message` - Send message
- `GET /api/v1/conversations/history/{call_id}` - Get history
- `WebSocket /api/v1/conversations/ws/{call_id}` - Real-time chat

### Knowledge Base
- `POST /api/v1/knowledge/documents` - Add document
- `GET /api/v1/knowledge/documents` - List all documents
- `POST /api/v1/knowledge/search` - Search documents
- `POST /api/v1/knowledge/upload` - Upload file
- `DELETE /api/v1/knowledge/documents/{doc_id}` - Delete document

## Configuration

### Environment Variables (`.env`)

```ini
# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000

# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Vector Database
VECTOR_DB_PATH=./data/chroma
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_TOP_K=3

# IVR Settings
MAX_RETRIES=3
CONVERSATION_TIMEOUT=300
```

### Settings in UI

Navigate to "Settings" section to configure:
- API Endpoint URL
- Request timeouts
- Retry limits
- View system information

## Knowledge Base System

### How RAG Works

1. **Document Ingestion**
   - Documents added to vector database
   - Text split into chunks (500 chars default)
   - Chunks converted to embeddings

2. **Semantic Search**
   - User query converted to embedding
   - Cosine similarity search in vector space
   - Top-K results retrieved (configurable)

3. **Context Augmentation**
   - Retrieved docs provided to AI agent
   - Agent uses docs to generate accurate responses
   - Relevance scores shown with results

### Best Practices

- **Document Quality**: Use clear, structured content
- **Categorization**: Properly categorize documents
- **Updates**: Keep knowledge base current
- **Testing**: Test with various queries

## Agent AI Features

### Intent Detection
Automatically detects:
- `billing` - Billing inquiries
- `technical` - Technical issues
- `account` - Account management
- `support` - General support requests
- `cancel` - Call cancellation
- `transfer` - Human agent requests

### Confidence Scoring
- Ranges from 0.0 to 1.0
- Based on context relevance
- Knowledge base match quality
- Response quality indicators

### Call Routing
- Automatically detects transfer needs
- Reasons for transfer included
- Seamless human handoff support

## Performance Optimization

### Tips for Better Performance

1. **Knowledge Base**
   - Keep documents focused and specific
   - Use appropriate chunk sizes
   - Regular cleanup of outdated docs

2. **Model Selection**
   - GPT-4 for complex reasoning
   - GPT-3.5 for faster responses
   - Adjust temperature (0.0-1.0)

3. **Caching**
   - Embed frequently used docs
   - Cache conversation contexts
   - Use WebSocket for real-time updates

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Must be 3.8+

# Check dependencies
pip list | grep -E "fastapi|langchain|chromadb"

# Verify OPENAI_API_KEY is set
echo $OPENAI_API_KEY
```

### API returns 500 errors
```
- Check logs in terminal
- Verify .env file configuration
- Check OpenAI API key validity
- Ensure all dependencies installed
```

### Frontend can't connect to backend
```
- Verify backend is running on port 8000
- Check CORS configuration
- Update API Endpoint in Settings
- Check browser console for errors
```

### Knowledge base not responding
```
- Verify data directory permissions
- Check available disk space
- Restart backend service
- Check Chroma database integrity
```

## Extension & Customization

### Add Custom Intent

Edit `services/agent_service.py`:
```python
intent_keywords = {
    "your_intent": ["keyword1", "keyword2"],
}
```

### Add Phone Integration

Update configuration:
```python
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Custom Embedding Model

In `config.py`:
```python
EMBEDDING_MODEL="your-preferred-model"
```

## Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t ivr-system .

# Run container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ivr-system
```

### Security Checklist
- [ ] Set DEBUG=False in production
- [ ] Use strong API keys
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Regular backups of knowledge base
- [ ] Monitor error logs

## Support & Community

For issues, feature requests, or contributions:
1. Check logs in `backend/` directory
2. Review API documentation at `/docs`
3. Test individual endpoints with curl or Postman

## License

This project is provided as-is for educational and commercial use.

## Version History

- **v1.0.0** (Current)
  - Initial release
  - FastAPI backend
  - RAG knowledge base
  - Modern web UI
  - Full call management

## Next Steps

1. ✅ Set up backend with your OpenAI API key
2. ✅ Build knowledge base with your documents
3. ✅ Test IVR with sample calls
4. ✅ Customize intents and routing
5. ✅ Deploy to production
6. ✅ Monitor and optimize

---

**Happy calling! 🎉**
