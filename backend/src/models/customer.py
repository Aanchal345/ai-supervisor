"""
Customer data model.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Customer(BaseModel):
    """
    Represents a customer in the system.
    """
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    
    # Interaction tracking
    total_calls: int = 0
    last_call_at: Optional[datetime] = None
    
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
    def from_dict(cls, data: dict) -> 'Customer':
        """Create instance from Firebase data."""
        datetime_fields = ['created_at', 'updated_at', 'last_call_at']
        for field in datetime_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)