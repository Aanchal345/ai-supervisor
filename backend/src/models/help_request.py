"""
Help Request data model with lifecycle management.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class RequestStatus(str, Enum):
    """Help request status lifecycle."""
    PENDING = "pending"
    RESOLVED = "resolved"
    TIMEOUT = "timeout"


class HelpRequest(BaseModel):
    """
    Represents a help request from AI agent to supervisor.
    
    Lifecycle: PENDING -> RESOLVED or TIMEOUT
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_phone: str
    customer_name: Optional[str] = None
    question: str
    context: Optional[str] = None  # Additional conversation context
    
    status: RequestStatus = RequestStatus.PENDING
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    
    # Supervisor response
    supervisor_answer: Optional[str] = None
    supervisor_id: Optional[str] = None
    
    # Follow-up tracking
    customer_notified: bool = False
    notification_sent_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firebase storage."""
        data = self.model_dump()
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HelpRequest':
        """Create instance from Firebase data."""
        # Convert ISO strings back to datetime
        datetime_fields = ['created_at', 'updated_at', 'resolved_at', 
                          'timeout_at', 'notification_sent_at']
        for field in datetime_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)


class HelpRequestCreate(BaseModel):
    """Schema for creating new help requests."""
    customer_phone: str
    customer_name: Optional[str] = None
    question: str
    context: Optional[str] = None


class HelpRequestResolve(BaseModel):
    """Schema for supervisor resolving a request."""
    supervisor_answer: str
    supervisor_id: Optional[str] = "supervisor_1"  # Default for Phase 1