"""Call management routes"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.models.schemas import (
    CallRequest, CallResponse, CallStatusResponse, CallState
)

router = APIRouter(prefix="/api/v1/calls", tags=["calls"])

# Global call manager instance
call_manager = None
agent_service = None


def get_dependencies():
    """Get service dependencies"""
    return {"call_manager": call_manager, "agent_service": agent_service}


@router.post("/initiate", response_model=CallResponse)
async def initiate_call(request: CallRequest):
    """Initiate a new call"""
    if not call_manager or not agent_service:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        # Create call
        call_data = call_manager.create_call(
            user_name=request.user_name,
            user_phone=request.user_phone,
            call_topic=request.call_topic
        )
        
        # Create agent context
        agent_service.create_call_context(
            call_id=call_data["call_id"],
            user_name=request.user_name,
            call_topic=request.call_topic
        )
        
        # Update call status
        call_manager.update_call_status(call_data["call_id"], CallState.CONNECTED)
        
        return CallResponse(
            call_id=call_data["call_id"],
            status=CallState.INITIATED,
            message=f"Call initiated for {request.user_name}. How can I help you today?",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{call_id}", response_model=CallStatusResponse)
async def get_call_status(call_id: str):
    """Get status of a call"""
    if not call_manager:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    call = call_manager.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return CallStatusResponse(
        call_id=call["call_id"],
        status=call["status"],
        duration=call["duration"],
        message_count=call["message_count"],
        created_at=call["created_at"],
        updated_at=call["updated_at"]
    )


@router.post("/end/{call_id}")
async def end_call(call_id: str):
    """End a call"""
    if not call_manager or not agent_service:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    call = call_manager.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    try:
        # End call in agent service
        agent_service.end_call(call_id)
        
        # Update call status
        call_manager.end_call(call_id)
        
        return {
            "call_id": call_id,
            "status": "ended",
            "duration": call["duration"],
            "message_count": call["message_count"],
            "message": "Call ended successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active")
async def get_active_calls():
    """Get all active calls"""
    if not call_manager:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    active = call_manager.get_active_calls()
    return {
        "count": len(active),
        "calls": [
            {
                "call_id": call["call_id"],
                "user_name": call["user_name"],
                "status": call["status"],
                "duration": call["duration"]
            }
            for call in active
        ]
    }
