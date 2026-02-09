"""Call Management Service"""
from typing import Dict, Optional, Any
from datetime import datetime
import uuid
from enum import Enum


class CallStatus(str, Enum):
    """Call status states"""
    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    ACTIVE = "active"
    ENDED = "ended"
    FAILED = "failed"


class CallManager:
    """Manages active calls and sessions"""
    
    def __init__(self):
        """Initialize call manager"""
        self.calls: Dict[str, Dict[str, Any]] = {}
    
    def create_call(self, user_name: str, user_phone: str, call_topic: str) -> Dict[str, Any]:
        """Create a new call"""
        call_id = f"call_{uuid.uuid4().hex[:12]}"
        
        call_data = {
            "call_id": call_id,
            "user_name": user_name,
            "user_phone": user_phone,
            "call_topic": call_topic,
            "status": CallStatus.INITIATED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "message_count": 0
        }
        
        self.calls[call_id] = call_data
        return call_data
    
    def get_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call details"""
        return self.calls.get(call_id)
    
    def update_call_status(self, call_id: str, status: CallStatus) -> bool:
        """Update call status"""
        if call_id not in self.calls:
            return False
        
        call = self.calls[call_id]
        call["status"] = status
        call["updated_at"] = datetime.now()
        
        if status == CallStatus.CONNECTED and not call["start_time"]:
            call["start_time"] = datetime.now()
        elif status == CallStatus.ENDED and not call["end_time"]:
            call["end_time"] = datetime.now()
            if call["start_time"]:
                call["duration"] = int((call["end_time"] - call["start_time"]).total_seconds())
        
        return True
    
    def increment_message_count(self, call_id: str) -> bool:
        """Increment message count for call"""
        if call_id not in self.calls:
            return False
        
        self.calls[call_id]["message_count"] += 1
        return True
    
    def end_call(self, call_id: str) -> bool:
        """End a call"""
        return self.update_call_status(call_id, CallStatus.ENDED)
    
    def get_active_calls(self) -> list:
        """Get all active calls"""
        return [
            call for call in self.calls.values()
            if call["status"] not in [CallStatus.ENDED, CallStatus.FAILED]
        ]
    
    def cleanup_old_calls(self, max_age_minutes: int = 60) -> int:
        """Remove calls older than specified time"""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        removed = 0
        
        call_ids_to_remove = [
            call_id for call_id, call in self.calls.items()
            if call["updated_at"] < cutoff_time and call["status"] == CallStatus.ENDED
        ]
        
        for call_id in call_ids_to_remove:
            del self.calls[call_id]
            removed += 1
        
        return removed
