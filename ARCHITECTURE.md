# IVR AI Agent System - Architecture Documentation

## System Overview

The IVR AI Agent System is a comprehensive, production-ready solution for handling customer interactions through intelligent AI agents. It combines multiple cutting-edge technologies to provide a seamless user experience.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Modern Web UI (HTML5, CSS3, JavaScript)                │  │
│  │  • Dashboard with real-time stats                       │  │
│  │  • Call management interface                            │  │
│  │  • Chat interface with message history                  │  │
│  │  • Knowledge base search and management                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                       │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │  Health &    │  Call        │  Conversation│  Knowledge   │ │
│  │  Status      │  Management  │  Management  │  Base        │ │
│  │  Endpoints   │  Endpoints   │  Endpoints   │  Endpoints   │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                              │
│  ┌──────────────┬──────────────┬──────────────────────┐        │
│  │ Call         │ Agent        │ RAG Service          │        │
│  │ Manager      │ Service      │ (Knowledge Base)     │        │
│  │              │              │                      │        │
│  │ • Create     │ • Process    │ • Document storage  │        │
│  │   calls      │   messages   │ • Semantic search   │        │
│  │ • Track      │ • Intent     │ • Relevance scoring │        │
│  │   status     │   detection  │                      │        │
│  │ • Manage     │ • Generate   │                      │        │
│  │   sessions   │   responses  │                      │        │
│  └──────────────┴──────────────┴──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┬──────────────┬──────────────────────┐        │
│  │ OpenAI       │ Sentence     │ ChromaDB             │        │
│  │ GPT-4        │ Transformers │ (Vector Storage)     │        │
│  │              │ (Embeddings) │                      │        │
│  │ • Text       │ • Convert    │ • Semantic search   │        │
│  │   generation │   docs to    │ • Vector similarity │        │
│  │ • Context    │   vectors    │                      │        │
│  │   awareness  │ • Embedding  │                      │        │
│  └──────────────┴──────────────┴──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Server**: Uvicorn (ASGI server)
- **LLM**: OpenAI GPT-4 (via LangChain)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: Chromadb (local vector database)
- **Data Validation**: Pydantic
- **Environment**: python-dotenv

### Frontend
- **HTML5**: Semantic structure
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Vanilla JS (no framework required)
- **Features**: WebSocket support, responsive design

### Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Hosting**: Any cloud platform (AWS, GCP, Azure, etc.)

## Data Flow

### Call Initiation Flow
```
User Input → API Endpoint → Call Manager → Agent Service → Response
   │                            │
   └──→ Session Created ────→ Conversation Context
                                │
                                └──→ RAG Service
                                     (Loaded for KB access)
```

### Message Processing Flow
```
Chat Message → API → Agent Service → LLM Prompt Construction
                        │
                        ├──→ RAG Service (Search KB)
                        │    └──→ Top-K Documents
                        │
                        ├──→ OpenAI API (Generate Response)
                        │    Input: [Prompt + KB Context]
                        │
                        └──→ Intent Detection → Response → UI
```

### Knowledge Base Flow
```
Add Document → File Upload/Form Input
                        │
                        ├──→ Text Chunking (500 chars)
                        │
                        ├──→ Embedding Generation
                        │    (Sentence Transformers)
                        │
                        └──→ Vector Storage (Chromadb)

Search Query → Embedding → Similarity Search → Top-K Results
               (Same Model) → Relevance Scoring → Return to User
```

## Component Details

### 1. Call Manager (`services/call_manager.py`)
**Responsibility**: Track and manage active calls

**Key Methods**:
- `create_call()` - Initialize new call session
- `get_call()` - Retrieve call data
- `update_call_status()` - Track call state changes
- `increment_message_count()` - Count messages in call
- `end_call()` - Finalize call and cleanup
- `get_active_calls()` - List ongoing calls

**Call States**:
- `INITIATED` - Call created
- `RINGING` - Alerting user
- `CONNECTED` - Established
- `ACTIVE` - In conversation
- `ENDED` - Completed
- `FAILED` - Error occurred

### 2. Agent AI Service (`services/agent_service.py`)
**Responsibility**: Handle conversational AI and intent detection

**Key Methods**:
- `create_call_context()` - Setup conversation context
- `process_user_message()` - Process and respond to messages
- `get_conversation()` - Retrieve conversation details
- `end_call()` - Generate call summary

**Features**:
- Conversation memory (buffer of last 6 messages)
- Intent detection from 8 categories
- Confidence scoring (0.0-1.0)
- Automatic transfer detection
- Call summary generation

### 3. RAG Service (`services/rag_service.py`)
**Responsibility**: Manage knowledge base and semantic search

**Key Methods**:
- `add_document()` - Add to knowledge base
- `retrieve_relevant_documents()` - Semantic search
- `search_documents()` - Query KB
- `get_all_documents()` - List all docs
- `delete_document()` - Remove doc
- `update_document()` - Modify doc

**RAG Process**:
1. Document ingestion with metadata
2. Chunking (configurable size)
3. Embedding with Sentence Transformers
4. Vector storage in Chromadb
5. Semantic similarity search

### 4. API Routes

**Health Routes** (`routes/health.py`)
- GET `/api/v1/health` - System status
- GET `/api/v1/status` - Operational status

**Call Routes** (`routes/calls.py`)
- POST `/api/v1/calls/initiate` - Start call
- GET `/api/v1/calls/status/{call_id}` - Call status
- POST `/api/v1/calls/end/{call_id}` - End call
- GET `/api/v1/calls/active` - List active calls

**Conversation Routes** (`routes/conversations.py`)
- POST `/api/v1/conversations/message` - Send message
- GET `/api/v1/conversations/history/{call_id}` - Get history
- WebSocket `/api/v1/conversations/ws/{call_id}` - Real-time

**Knowledge Base Routes** (`routes/knowledge.py`)
- POST `/api/v1/knowledge/documents` - Add doc
- GET `/api/v1/knowledge/documents` - List docs
- POST `/api/v1/knowledge/search` - Search
- POST `/api/v1/knowledge/upload` - Upload file
- DELETE `/api/v1/knowledge/documents/{doc_id}` - Delete

## Configuration

### Environment Variables
```
DEBUG                   - Enable debug mode
HOST, PORT             - Server binding
OPENAI_API_KEY         - LLM API key
OPENAI_MODEL           - Model selection
VECTOR_DB_PATH         - KB storage location
EMBEDDING_MODEL        - Embedding model name
CHUNK_SIZE, OVERLAP    - Document chunking params
RETRIEVAL_TOP_K        - Search result count
MAX_RETRIES            - Retry attempts
CONVERSATION_TIMEOUT   - Session timeout
```

### Pydantic Models (`models/schemas.py`)
- `CallRequest` / `CallResponse`
- `ConversationMessage` / `ConversationResponse`
- `DocumentRequest` / `SearchResponse`
- `HealthResponse` / `ErrorResponse`

## Performance Characteristics

### Latency
- Call initiation: ~100ms
- Message processing: 1-3s (depends on LLM)
- Knowledge search: 50-200ms
- Document upload: <1s

### Scalability
- Current: Single instance, in-memory sessions
- Horizontal: Add load balancer + shared session store
- Vertical: Increase timeouts, optimize chunks

### Resource Usage
- RAM: ~500MB (includes models)
- CPU: Variable (depends on concurrent calls)
- Disk: ~100MB (embeddings) + KB size

## Error Handling

### API Error Responses
```json
{
    "error_code": "CALL_NOT_FOUND",
    "message": "The specified call does not exist",
    "details": {"call_id": "invalid_id"},
    "timestamp": "2024-02-09T10:00:00"
}
```

### Common Errors
- 400: Bad request (validation error)
- 404: Resource not found
- 500: Server error (check logs)

## Security Considerations

### Current Implementation
- CORS enabled for all origins (production: restrict)
- Environment variables for API keys
- Input validation via Pydantic
- No authentication layer (add for production)

### Recommendations
1. Implement JWT authentication
2. Add rate limiting
3. Use HTTPS/TLS
4. Validate all inputs
5. Sanitize LLM outputs
6. Log all API calls
7. Monitor for abuse
8. Regular security audits

## Testing Strategy

### Unit Tests
- Test each service independently
- Mock external APIs
- Validate data models

### Integration Tests
- End-to-end call flow
- Message processing
- Knowledge base operations

### Performance Tests
- Load testing with 100+ concurrent calls
- Knowledge base scalability
- API response times

## Monitoring & Logging

### Metrics to Track
- Active calls count
- Average call duration
- Message processing time
- KB search relevance
- Error rates
- API response times
- System resource usage

### Logging
- Structured logging with levels
- Request/response logging
- Error stack traces
- Performance metrics

## Future Enhancements

1. **Phone Integration**
   - Twilio integration
   - Real voice support
   - Recording capability

2. **Advanced AI**
   - Multi-language support
   - Sentiment analysis
   - Emotion detection

3. **Analytics**
   - Call transcripts
   - Performance dashboards
   - Customer satisfaction tracking

4. **Integration**
   - CRM systems
   - Ticketing systems
   - Database backends

5. **Optimization**
   - Caching layer
   - Async processing
   - Worker queues

## Conclusion

This architecture provides a robust, scalable foundation for IVR systems. The modular design allows for easy extensions and customizations while maintaining code quality and performance.
