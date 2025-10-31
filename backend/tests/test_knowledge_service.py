"""
Unit tests for knowledge service.
"""
import pytest
from src.models.knowledge_base import KnowledgeCreate
from src.services.knowledge_service import knowledge_service


def test_add_knowledge_entry():
    """Test adding a knowledge entry."""
    entry_data = KnowledgeCreate(
        question="Test question?",
        answer="Test answer",
        category="test",
        keywords=["test", "sample"]
    )
    
    entry = knowledge_service.add_entry(entry_data)
    
    assert entry.entry_id is not None
    assert entry.question == "Test question?"
    assert "test" in entry.keywords


def test_search_knowledge():
    """Test searching knowledge base."""
    results = knowledge_service.search_knowledge("hours", limit=5)
    
    assert isinstance(results, list)
    assert len(results) <= 5