"""
Knowledge Base entry model for learned answers.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class KnowledgeEntry(BaseModel):
    """
    Represents a learned answer in the knowledge base.
    """
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    
    # Categorization for better retrieval
    category: Optional[str] = None  # e.g., "hours", "services", "pricing"
    keywords: List[str] = Field(default_factory=list)
    
    # Metadata
    source: str = "supervisor"  # Where this knowledge came from
    source_request_id: Optional[str] = None  # Link back to help request
    confidence: float = 1.0  # How confident we are in this answer
    
    # Usage tracking
    times_used: int = 0
    last_used_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firebase storage."""
        data = self.model_dump()
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KnowledgeEntry':
        """Create instance from Firebase data."""
        datetime_fields = ['created_at', 'updated_at', 'last_used_at']
        for field in datetime_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)


class KnowledgeCreate(BaseModel):
    """Schema for creating new knowledge entries."""
    question: str
    answer: str
    category: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    source_request_id: Optional[str] = None