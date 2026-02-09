"""Agent AI Service for conversational AI"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import uuid
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os


class AgentAIService:
    """Handles AI agent conversations with RAG integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", rag_service=None):
        """Initialize agent AI service"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.rag_service = rag_service
        
        # Initialize LLM only if API key is available
        if self.api_key:
            self.llm = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=model,
                temperature=0.7,
                max_tokens=500
            )
        else:
            self.llm = None
        
        # Store conversation contexts
        self.conversations: Dict[str, Dict[str, Any]] = {}
    
    def create_call_context(self, call_id: str, user_name: str, call_topic: str) -> Dict[str, Any]:
        """Create a new call context for conversation tracking"""
        context = {
            "call_id": call_id,
            "user_name": user_name,
            "call_topic": call_topic,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "intent": None,
            "extracted_info": {}
        }
        self.conversations[call_id] = context
        return context
    
    def process_user_message(self, call_id: str, user_message: str) -> Dict[str, Any]:
        """Process user message and generate agent response"""
        if call_id not in self.conversations:
            return {
                "error": "Call not found",
                "message": "Please create a call context first"
            }
        
        context = self.conversations[call_id]
        
        # Add user message to history
        context["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Detect intent
        intent = self._detect_intent(user_message)
        context["intent"] = intent
        
        # Retrieve relevant documents if RAG available
        retrieved_docs = []
        if self.rag_service:
            retrieved_docs = self.rag_service.retrieve_relevant_documents(user_message, top_k=3)
        
        # Generate response
        if self.llm:
            agent_response = self._generate_response_with_llm(user_message, intent, retrieved_docs)
        else:
            agent_response = self._generate_response_without_llm(user_message, intent, retrieved_docs)
        
        # Add agent response to history
        context["messages"].append({
            "role": "agent",
            "content": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "call_id": call_id,
            "user_message": user_message,
            "agent_response": agent_response,
            "intent": intent,
            "retrieved_documents": retrieved_docs,
            "message_count": len(context["messages"])
        }
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        intent_keywords = {
            "billing": ["bill", "charge", "payment", "invoice", "fee", "cost", "refund"],
            "technical": ["issue", "error", "problem", "not working", "broken", "help", "bug"],
            "account": ["password", "login", "account", "username", "access", "profile"],
            "product": ["product", "feature", "update", "version", "new", "release"],
            "sales": ["buy", "purchase", "order", "price", "discount", "promotion", "deal"],
            "support": ["help", "support", "assist", "guide", "how to", "tutorial"],
            "complaint": ["angry", "disappointed", "unhappy", "complaint", "bad", "terrible"],
            "other": []
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "other"
    
    def _generate_response_with_llm(self, user_message: str, intent: str, retrieved_docs: List[Dict]) -> str:
        """Generate response using LLM"""
        try:
            # Build context from retrieved documents
            context = ""
            if retrieved_docs:
                context = "\n\nRelevant Information:\n"
                for doc in retrieved_docs:
                    context += f"- {doc['title']}: {doc['content'][:200]}...\n"
            
            # Create prompt
            prompt = f"""You are a helpful IVR assistant. You detected the user's intent as: {intent}

User Message: {user_message}
{context}

Provide a helpful, concise response (max 200 characters):"""
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return self._generate_response_without_llm(user_message, intent, retrieved_docs)
    
    def _generate_response_without_llm(self, user_message: str, intent: str, retrieved_docs: List[Dict]) -> str:
        """Generate response without LLM (fallback)"""
        responses = {
            "billing": "I can help you with billing questions. We offer flexible payment options and refunds within 30 days.",
            "technical": "For technical issues, please ensure you have the latest version. Contact our support team for assistance.",
            "account": "For account security, please verify your identity through our secure portal.",
            "product": "Our products include comprehensive features. Visit our website for the latest updates.",
            "sales": "We offer competitive pricing and special discounts for bulk orders. Contact sales for details.",
            "support": "Our support team is available 24/7. How can I assist you further?",
            "complaint": "We apologize for your experience. We're committed to resolving this. Could you provide more details?",
            "other": "Thank you for your message. How can I assist you today?"
        }
        
        response = responses.get(intent, responses["other"])
        
        # Add info from retrieved documents
        if retrieved_docs:
            response += f" Found {len(retrieved_docs)} relevant resources."
        
        return response
    
    def get_conversation_summary(self, call_id: str) -> Dict[str, Any]:
        """Get summary of conversation"""
        if call_id not in self.conversations:
            return {"error": "Call not found"}
        
        context = self.conversations[call_id]
        
        return {
            "call_id": call_id,
            "user_name": context["user_name"],
            "call_topic": context["call_topic"],
            "created_at": context["created_at"],
            "intent": context["intent"],
            "message_count": len(context["messages"]),
            "messages": context["messages"]
        }
    
    def end_call(self, call_id: str) -> Dict[str, Any]:
        """End a call and get summary"""
        if call_id not in self.conversations:
            return {"error": "Call not found"}
        
        context = self.conversations[call_id]
        summary = {
            "call_id": call_id,
            "user_name": context["user_name"],
            "call_topic": context["call_topic"],
            "created_at": context["created_at"],
            "ended_at": datetime.now().isoformat(),
            "duration_seconds": 300,  # Placeholder
            "intent_detected": context["intent"],
            "total_messages": len(context["messages"])
        }
        
        # Remove from active conversations
        del self.conversations[call_id]
        
        return summary
    
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """Get list of active calls"""
        return [
            {
                "call_id": call_id,
                "user_name": context["user_name"],
                "call_topic": context["call_topic"],
                "created_at": context["created_at"],
                "message_count": len(context["messages"])
            }
            for call_id, context in self.conversations.items()
        ]

    def get_conversation(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Return the raw conversation context for a given call_id"""
        return self.conversations.get(call_id)
