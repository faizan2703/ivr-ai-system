"""Conversation routes for message handling"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from datetime import datetime
from app.models.schemas import (
    ConversationRequest, ConversationResponse, ConversationHistoryResponse,
    ConversationMessage, MessageType
)

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

# Service instances
call_manager = None
agent_service = None
call_manager_instance = None


class ConnectionManager:
    """WebSocket connection manager"""
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, call_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[call_id] = websocket

    def disconnect(self, call_id: str):
        if call_id in self.active_connections:
            del self.active_connections[call_id]

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except:
                pass


connection_manager = ConnectionManager()


@router.post("/message", response_model=ConversationResponse)
async def send_message(request: ConversationRequest):
    """Send message in conversation"""
    if not agent_service or not call_manager:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    # Check if call exists
    call = call_manager.get_call(request.call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    try:
        # Process message with agent
        response = agent_service.process_user_message(
            call_id=request.call_id,
            user_message=request.message
        )
        
        # Update message count
        call_manager.increment_message_count(request.call_id)
        
        return ConversationResponse(
            call_id=request.call_id,
            agent_response=response.get("agent_response", ""),
            intent=response.get("intent", ""),
            confidence=response.get("confidence", 0.0),
            requires_transfer=response.get("requires_transfer", False),
            transfer_reason=response.get("transfer_reason"),
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{call_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(call_id: str):
    """Get conversation history"""
    if not agent_service:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    conversation = agent_service.get_conversation(call_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Convert messages to proper format
    messages = [
        ConversationMessage(
            id=f"{msg.get('type')}_{i}",
            message_type=MessageType.USER if msg["type"] == "user" else MessageType.AGENT,
            content=msg["content"],
            timestamp=datetime.fromisoformat(msg["timestamp"])
        )
        for i, msg in enumerate(conversation["messages"])
    ]
    
    return ConversationHistoryResponse(
        call_id=call_id,
        messages=messages,
        summary=conversation.get("summary", "No summary available"),
        call_status="active"
    )


@router.websocket("/ws/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for real-time conversation"""
    if not agent_service or not call_manager:
        await websocket.close(code=1011, reason="Services not initialized")
        return
    
    # Check if call exists
    call = call_manager.get_call(call_id)
    if not call:
        await websocket.close(code=1008, reason="Call not found")
        return
    
    await connection_manager.connect(call_id, websocket)
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            
            # Process message
            response = agent_service.process_user_message(call_id, message)
            call_manager.increment_message_count(call_id)
            
            # Send response back
            await websocket.send_json({
                "type": "response",
                "agent_response": response.get("agent_response", ""),
                "intent": response.get("intent", ""),
                "confidence": response.get("confidence", 0.0),
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        connection_manager.disconnect(call_id)
        print(f"Client disconnected from call {call_id}")
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
        connection_manager.disconnect(call_id)
