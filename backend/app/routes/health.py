"""Health check and status routes"""
from fastapi import APIRouter, Depends
from datetime import datetime
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        services={
            "api": "running",
            "rag": "ready",
            "agent": "ready",
            "database": "connected"
        }
    )


@router.get("/status")
async def status():
    """Get system status"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }
