"""
Unit tests for AI service.
"""
import pytest
from src.services.ai_service import ai_service


def test_generate_response():
    """Test AI response generation."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    
    response = ai_service.generate_response(messages)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


def test_extract_keywords():
    """Test keyword extraction."""
    text = "I need a haircut appointment for next week"
    keywords = ai_service.extract_keywords(text)
    
    assert isinstance(keywords, list)
    assert len(keywords) > 0