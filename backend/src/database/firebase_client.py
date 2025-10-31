"""
Firebase database client with CRUD operations.
"""
from typing import Optional, List, Dict, Any
from src.config.firebase_config import firebase_config
from src.utils.logger import logger


class FirebaseClient:
    """
    Wrapper around Firebase Realtime Database with clean API.
    
    Database structure:
    /help_requests/{request_id}
    /knowledge_base/{entry_id}
    /customers/{phone_number}
    """
    
    def __init__(self):
        self.db = firebase_config.get_database()
    
    # Help Requests Operations
    def create_help_request(self, request_id: str, data: dict) -> bool:
        """Create a new help request."""
        try:
            ref = self.db.child('help_requests').child(request_id)
            ref.set(data)
            logger.info(f"Created help request: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create help request: {str(e)}")
            return False
    
    def get_help_request(self, request_id: str) -> Optional[dict]:
        """Get a specific help request."""
        try:
            ref = self.db.child('help_requests').child(request_id)
            data = ref.get()
            return data
        except Exception as e:
            logger.error(f"Failed to get help request {request_id}: {str(e)}")
            return None
    
    def update_help_request(self, request_id: str, updates: dict) -> bool:
        """Update an existing help request."""
        try:
            ref = self.db.child('help_requests').child(request_id)
            ref.update(updates)
            logger.info(f"Updated help request: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update help request: {str(e)}")
            return False
    
    def get_all_help_requests(self, status: Optional[str] = None) -> List[dict]:
        """Get all help requests, optionally filtered by status."""
        try:
            ref = self.db.child('help_requests')
            data = ref.get() or {}
            
            requests = []
            for request_id, request_data in data.items():
                if status is None or request_data.get('status') == status:
                    request_data['request_id'] = request_id
                    requests.append(request_data)
            
            return requests
        except Exception as e:
            logger.error(f"Failed to get help requests: {str(e)}")
            return []
    
    # Knowledge Base Operations
    def create_knowledge_entry(self, entry_id: str, data: dict) -> bool:
        """Add a new entry to the knowledge base."""
        try:
            ref = self.db.child('knowledge_base').child(entry_id)
            ref.set(data)
            logger.info(f"Created knowledge entry: {entry_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create knowledge entry: {str(e)}")
            return False
    
    def get_knowledge_entry(self, entry_id: str) -> Optional[dict]:
        """Get a specific knowledge entry."""
        try:
            ref = self.db.child('knowledge_base').child(entry_id)
            return ref.get()
        except Exception as e:
            logger.error(f"Failed to get knowledge entry: {str(e)}")
            return None
    
    def get_all_knowledge(self) -> List[dict]:
        """Get all knowledge base entries."""
        try:
            ref = self.db.child('knowledge_base')
            data = ref.get() or {}
            
            entries = []
            for entry_id, entry_data in data.items():
                entry_data['entry_id'] = entry_id
                entries.append(entry_data)
            
            return entries
        except Exception as e:
            logger.error(f"Failed to get knowledge base: {str(e)}")
            return []
    
    def update_knowledge_entry(self, entry_id: str, updates: dict) -> bool:
        """Update a knowledge entry (e.g., increment usage count)."""
        try:
            ref = self.db.child('knowledge_base').child(entry_id)
            ref.update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update knowledge entry: {str(e)}")
            return False
    
    # Customer Operations (for tracking)
    def save_customer_info(self, phone: str, data: dict) -> bool:
        """Save or update customer information."""
        try:
            # Sanitize phone number for Firebase key
            safe_phone = phone.replace('+', '_').replace(' ', '')
            ref = self.db.child('customers').child(safe_phone)
            ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Failed to save customer info: {str(e)}")
            return False
    
    def get_customer_info(self, phone: str) -> Optional[dict]:
        """Get customer information."""
        try:
            safe_phone = phone.replace('+', '_').replace(' ', '')
            ref = self.db.child('customers').child(safe_phone)
            return ref.get()
        except Exception as e:
            logger.error(f"Failed to get customer info: {str(e)}")
            return None


# Global client instance
firebase_client = FirebaseClient()