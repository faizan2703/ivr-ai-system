"""RAG (Retrieval Augmented Generation) Service for Knowledge Base"""
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from collections import Counter
import math


class RAGService:
    """Handles RAG operations with lightweight text-based search (compatible with Python 3.14+)"""
    
    def __init__(self, db_path: str = "./data/kb", embedding_model: str = None):
        """Initialize RAG service with in-memory vector storage"""
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        # In-memory storage
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.word_index: Dict[str, List[str]] = {}  # Inverted index for fast search
        
        # Load existing documents if available
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Load documents from persistent storage"""
        try:
            docs_file = os.path.join(self.db_path, "documents.json")
            
            if os.path.exists(docs_file):
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
                    # Rebuild word index
                    for doc_id, doc in self.documents.items():
                        self._index_document(doc_id, doc["content"])
        except Exception as e:
            print(f"Warning: Could not load documents from disk: {e}")
    
    def _save_to_disk(self):
        """Save documents to persistent storage"""
        try:
            docs_file = os.path.join(self.db_path, "documents.json")
            
            with open(docs_file, 'w') as f:
                json.dump(self.documents, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save documents to disk: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        import re
        # Convert to lowercase and split by non-alphanumeric characters
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def _index_document(self, doc_id: str, content: str):
        """Build inverted index for fast searching"""
        words = self._tokenize(content)
        for word in set(words):  # Use set to avoid duplicates
            if word not in self.word_index:
                self.word_index[word] = []
            if doc_id not in self.word_index[word]:
                self.word_index[word].append(doc_id)
    
    def _calculate_tfidf_score(self, query_words: List[str], doc_id: str) -> float:
        """Calculate TF-IDF-like score for a document"""
        if doc_id not in self.documents:
            return 0.0
        
        doc_content = self.documents[doc_id]["content"].lower()
        score = 0.0
        
        for word in query_words:
            # Count occurrences in document
            word_count = len([w for w in self._tokenize(doc_content) if w == word])
            if word_count > 0:
                # Simple scoring: term frequency * inverse document frequency
                idf = math.log(len(self.documents) / (len(self.word_index.get(word, [])) + 1))
                tf = word_count / len(self._tokenize(doc_content)) if doc_content else 0
                score += tf * idf
        
        return score
    
    def add_document(self, title: str, content: str, category: str = "general", 
                    tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        doc_id = str(uuid.uuid4())
        
        # Create metadata
        metadata = {
            "title": title,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "tags": tags or []
        }
        
        # Store document
        self.documents[doc_id] = {
            "id": doc_id,
            "title": title,
            "content": content,
            "metadata": metadata
        }
        
        # Index the document
        self._index_document(doc_id, content)
        
        # Persist to disk
        self._save_to_disk()
        
        return {
            "document_id": doc_id,
            "title": title,
            "category": category,
            "created_at": metadata["created_at"],
            "message": f"Document '{title}' added successfully"
        }
    
    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant documents based on query using TF-IDF scoring"""
        if not self.documents:
            return []
        
        # Tokenize query
        query_words = self._tokenize(query)
        if not query_words:
            return []
        
        # Calculate scores for all documents
        scores = {}
        for doc_id in self.documents.keys():
            scores[doc_id] = self._calculate_tfidf_score(query_words, doc_id)
        
        # Sort by score and return top k
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        retrieved_docs = []
        for doc_id, score in sorted_docs[:top_k]:
            if score > 0:  # Only include documents with positive scores
                doc = self.documents[doc_id]
                retrieved_docs.append({
                    "document_id": doc_id,
                    "title": doc["title"],
                    "content": doc["content"],
                    "relevance_score": round(min(score, 1.0), 4),
                    "category": doc["metadata"]["category"]
                })
        
        return retrieved_docs
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search documents in knowledge base"""
        return self.retrieve_relevant_documents(query, top_k)
    
    def get_all_documents(self) -> Dict[str, Any]:
        """Get all documents from knowledge base"""
        documents = []
        categories = set()
        
        for doc_id, doc in self.documents.items():
            category = doc["metadata"]["category"]
            categories.add(category)
            
            documents.append({
                "document_id": doc_id,
                "title": doc["title"],
                "category": category,
                "created_at": doc["metadata"]["created_at"],
                "preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            })
        
        return {
            "documents": documents,
            "total": len(documents),
            "categories": list(categories)
        }
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from knowledge base"""
        try:
            if doc_id in self.documents:
                # Remove from word index
                doc_content = self.documents[doc_id]["content"]
                words = self._tokenize(doc_content)
                for word in set(words):
                    if word in self.word_index and doc_id in self.word_index[word]:
                        self.word_index[word].remove(doc_id)
                    if not self.word_index[word]:
                        del self.word_index[word]
                
                del self.documents[doc_id]
            
            self._save_to_disk()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def update_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Update a document in knowledge base"""
        try:
            if doc_id not in self.documents:
                return False
            
            # Remove old indexed words
            old_content = self.documents[doc_id]["content"]
            old_words = self._tokenize(old_content)
            for word in set(old_words):
                if word in self.word_index and doc_id in self.word_index[word]:
                    self.word_index[word].remove(doc_id)
                if not self.word_index[word]:
                    del self.word_index[word]
            
            # Update document
            self.documents[doc_id]["content"] = content
            if metadata:
                self.documents[doc_id]["metadata"].update(metadata)
            
            # Re-index with new content
            self._index_document(doc_id, content)
            
            self._save_to_disk()
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
