"""
IVR AI Agent System - API Testing & Demo Script
This script provides easy testing of all API endpoints
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class IVRSystemTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.call_id = None
        self.session = requests.Session()
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with level indicators"""
        levels = {"SUCCESS": "✓", "ERROR": "✗", "INFO": "ℹ", "CALL": "📞"}
        print(f"{levels.get(level, '•')} {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code >= 200 and response.status_code < 300:
                return response.json() if response.text else {}
            else:
                self.log(f"HTTP {response.status_code}: {response.text}", "ERROR")
                return None
        
        except requests.exceptions.ConnectionError:
            self.log("Cannot connect to backend. Is it running?", "ERROR")
            return None
        except Exception as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None
    
    def test_health(self):
        """Test API health endpoint"""
        self.log("Testing API Health...", "INFO")
        result = self.make_request("GET", "/api/v1/health")
        if result:
            self.log(f"Backend Status: {result.get('status', 'unknown')}", "SUCCESS")
            return True
        return False
    
    def test_initiate_call(self):
        """Test call initiation"""
        self.log("Initiating test call...", "CALL")
        data = {
            "user_name": "Test User",
            "user_phone": "+1234567890",
            "call_topic": "billing",
            "language": "en"
        }
        result = self.make_request("POST", "/api/v1/calls/initiate", data)
        if result and "call_id" in result:
            self.call_id = result["call_id"]
            self.log(f"Call Initiated: {self.call_id}", "SUCCESS")
            self.log(f"Message: {result.get('message', '')}", "INFO")
            return True
        return False
    
    def test_call_status(self):
        """Test get call status"""
        if not self.call_id:
            self.log("No active call", "ERROR")
            return False
        
        self.log("Checking call status...", "INFO")
        result = self.make_request("GET", f"/api/v1/calls/status/{self.call_id}")
        if result:
            self.log(f"Call Status: {result.get('status', 'unknown')}", "SUCCESS")
            self.log(f"Duration: {result.get('duration', 0)}s", "INFO")
            return True
        return False
    
    def test_send_message(self, message: str):
        """Test sending message in conversation"""
        if not self.call_id:
            self.log("No active call", "ERROR")
            return False
        
        self.log(f"Sending message: '{message}'", "INFO")
        data = {
            "call_id": self.call_id,
            "message": message
        }
        result = self.make_request("POST", "/api/v1/conversations/message", data)
        if result:
            agent_response = result.get("agent_response", "")
            intent = result.get("intent", "unknown")
            confidence = result.get("confidence", 0)
            
            self.log(f"Agent Response: {agent_response}", "SUCCESS")
            self.log(f"Detected Intent: {intent} (confidence: {confidence:.0%})", "INFO")
            return True
        return False
    
    def test_add_document(self):
        """Test adding document to knowledge base"""
        self.log("Adding document to knowledge base...", "INFO")
        data = {
            "title": "Test FAQ",
            "content": "This is a test document. Q: What is this? A: This is a test.",
            "category": "general",
            "tags": ["test", "demo"]
        }
        result = self.make_request("POST", "/api/v1/knowledge/documents", data)
        if result and "document_id" in result:
            self.log(f"Document Added: {result['document_id']}", "SUCCESS")
            return True
        return False
    
    def test_search_documents(self):
        """Test searching knowledge base"""
        self.log("Searching knowledge base...", "INFO")
        data = {
            "query": "test",
            "top_k": 3
        }
        result = self.make_request("POST", "/api/v1/knowledge/search", data)
        if result:
            total_results = result.get("total_results", 0)
            self.log(f"Found {total_results} results", "SUCCESS")
            for i, doc in enumerate(result.get("results", [])[:3], 1):
                relevance = doc.get("relevance_score", 0)
                self.log(f"{i}. {doc.get('title', 'Unknown')} (relevance: {relevance:.0%})", "INFO")
            return True
        return False
    
    def test_list_documents(self):
        """Test listing all documents"""
        self.log("Listing all documents...", "INFO")
        result = self.make_request("GET", "/api/v1/knowledge/documents")
        if result:
            total = result.get("total", 0)
            self.log(f"Total Documents: {total}", "SUCCESS")
            categories = result.get("categories", [])
            if categories:
                self.log(f"Categories: {', '.join(categories)}", "INFO")
            return True
        return False
    
    def test_conversation_history(self):
        """Test getting conversation history"""
        if not self.call_id:
            self.log("No active call", "ERROR")
            return False
        
        self.log("Retrieving conversation history...", "INFO")
        result = self.make_request("GET", f"/api/v1/conversations/history/{self.call_id}")
        if result:
            messages = result.get("messages", [])
            self.log(f"Messages in conversation: {len(messages)}", "SUCCESS")
            for msg in messages:
                msg_type = msg.get("message_type", "unknown")
                content = msg.get("content", "")[:50] + "..."
                self.log(f"{msg_type.upper()}: {content}", "INFO")
            return True
        return False
    
    def test_active_calls(self):
        """Test getting active calls"""
        self.log("Getting active calls...", "INFO")
        result = self.make_request("GET", "/api/v1/calls/active")
        if result:
            count = result.get("count", 0)
            self.log(f"Active Calls: {count}", "SUCCESS")
            for call in result.get("calls", [])[:5]:
                self.log(f"  - {call.get('user_name', 'Unknown')}: {call.get('status', 'unknown')}", "INFO")
            return True
        return False
    
    def test_end_call(self):
        """Test ending call"""
        if not self.call_id:
            self.log("No active call", "ERROR")
            return False
        
        self.log("Ending call...", "CALL")
        result = self.make_request("POST", f"/api/v1/calls/end/{self.call_id}")
        if result:
            self.log(f"Call ended successfully", "SUCCESS")
            self.log(f"Total Messages: {result.get('message_count', 0)}", "INFO")
            self.log(f"Duration: {result.get('duration', 0)}s", "INFO")
            self.call_id = None
            return True
        return False
    
    def run_full_demo(self):
        """Run complete demo of all features"""
        print("\n" + "="*50)
        print("IVR AI Agent System - Full Demo")
        print("="*50 + "\n")
        
        # Test health
        if not self.test_health():
            self.log("Cannot proceed - backend not responding", "ERROR")
            return
        
        print()
        
        # Test knowledge base
        self.test_list_documents()
        print()
        
        # Initiate call
        if not self.test_initiate_call():
            return
        print()
        
        # Send messages
        test_messages = [
            "Hello, I need help with my billing",
            "How can I check my current bill?",
            "What are the payment methods?"
        ]
        
        for msg in test_messages:
            self.test_send_message(msg)
            time.sleep(1)  # Small delay between messages
            print()
        
        # Check conversation history
        self.test_conversation_history()
        print()
        
        # Check active calls
        self.test_active_calls()
        print()
        
        # End call
        self.test_end_call()
        
        print("\n" + "="*50)
        print("Demo Complete!")
        print("="*50 + "\n")


def main():
    """Main entry point"""
    import sys
    
    tester = IVRSystemTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "health":
            tester.test_health()
        elif command == "demo":
            tester.run_full_demo()
        elif command == "call":
            tester.test_initiate_call()
        elif command == "message":
            if len(sys.argv) > 2:
                msg = " ".join(sys.argv[2:])
                tester.test_send_message(msg)
            else:
                print("Usage: python test_api.py message <your message>")
        elif command == "docs":
            tester.test_list_documents()
        elif command == "search":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                data = {"query": query, "top_k": 5}
                result = tester.make_request("POST", "/api/v1/knowledge/search", data)
                if result:
                    print(json.dumps(result, indent=2))
            else:
                print("Usage: python test_api.py search <query>")
        else:
            print("Unknown command. Use 'demo' to run full demo.")
    else:
        print("IVR AI Agent System - API Tester")
        print("Usage: python test_api.py [command] [args]")
        print("\nCommands:")
        print("  health              - Check API health")
        print("  demo                - Run full feature demo")
        print("  call                - Initiate a test call")
        print("  message <text>      - Send message in active call")
        print("  docs                - List all documents")
        print("  search <query>      - Search knowledge base")
        print("\nExample:")
        print("  python test_api.py demo")
        print("  python test_api.py message How do I reset my password?")
        print("  python test_api.py search billing faq")


if __name__ == "__main__":
    main()
