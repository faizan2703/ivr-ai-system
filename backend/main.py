"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.agent_service import AgentAIService
from app.services.call_manager import CallManager
from app.routes import health, calls, conversations, knowledge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
rag_service = None
agent_service = None
call_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global rag_service, agent_service, call_manager
    
    logger.info("Initializing services...")
    
    try:
        # Initialize RAG service
        rag_service = RAGService(
            db_path=settings.VECTOR_DB_PATH,
            embedding_model=settings.EMBEDDING_MODEL
        )
        logger.info("✓ RAG service initialized")
        
        # Initialize call manager
        call_manager = CallManager()
        logger.info("✓ Call manager initialized")
        
        # Initialize agent AI service
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠ OpenAI API key not set. Agent will have limited functionality.")
            agent_service = AgentAIService(
                api_key="test-key",
                model=settings.OPENAI_MODEL,
                rag_service=rag_service
            )
        else:
            agent_service = AgentAIService(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                rag_service=rag_service
            )
        logger.info("✓ Agent AI service initialized")
        
        # Inject services into routes
        health.router.app = app
        calls.call_manager = call_manager
        calls.agent_service = agent_service
        conversations.call_manager = call_manager
        conversations.agent_service = agent_service
        knowledge.rag_service = rag_service
        
        logger.info("✓ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise
    
    yield
    
    logger.info("Shutting down services...")
    # Cleanup if needed
    logger.info("✓ Services shut down")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="IVR Agent AI System with RAG Knowledge Base",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(calls.router)
app.include_router(conversations.router)
app.include_router(knowledge.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
