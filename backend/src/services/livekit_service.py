"""
LiveKit service for managing voice agent connections.
"""
from typing import Optional, Dict
from src.config.settings import settings
from src.utils.logger import logger


class LiveKitService:
    """
    Handles LiveKit room management and agent connections.
    """
    
    def __init__(self):
        self.url = settings.livekit_url
        self.api_key = settings.livekit_api_key
        self.api_secret = settings.livekit_api_secret
        self.active_sessions: Dict[str, dict] = {}
    
    def create_session(self, customer_phone: str) -> str:
        """
        Create a new LiveKit session for a customer.
        
        Args:
            customer_phone: Customer's phone number
        
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            'customer_phone': customer_phone,
            'started_at': None,
            'ended_at': None
        }
        
        logger.info(f"Created LiveKit session: {session_id}")
        return session_id
    
    def end_session(self, session_id: str) -> bool:
        """
        End a LiveKit session.
        
        Args:
            session_id: Session to end
        
        Returns:
            True if successful
        """
        if session_id in self.active_sessions:
            from datetime import datetime
            self.active_sessions[session_id]['ended_at'] = datetime.utcnow()
            logger.info(f"Ended LiveKit session: {session_id}")
            return True
        return False
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get information about a session."""
        return self.active_sessions.get(session_id)


# Global service instance
livekit_service = LiveKitService()