"""
Knowledge Base API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from src.models.knowledge_base import KnowledgeEntry, KnowledgeCreate
from src.services.knowledge_service import knowledge_service
from src.utils.logger import logger

router = APIRouter(redirect_slashes=False)  # Added this parameter


@router.get("/", response_model=List[KnowledgeEntry])
async def get_all_knowledge():
    """
    Get all entries in the knowledge base.
    
    Used by supervisor UI to view learned answers.
    """
    try:
        entries = knowledge_service.get_all_knowledge()
        return entries
    except Exception as e:
        logger.error(f"Failed to get knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch knowledge base")


@router.get("/search", response_model=List[KnowledgeEntry])
async def search_knowledge(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Max results")
):
    """
    Search knowledge base for relevant entries.
    
    Used by AI agent to find answers.
    """
    try:
        results = knowledge_service.search_knowledge(query, limit)
        return results
    except Exception as e:
        logger.error(f"Failed to search knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/", response_model=KnowledgeEntry, status_code=201)
async def create_knowledge_entry(entry_data: KnowledgeCreate):
    """
    Manually add an entry to the knowledge base.
    
    Optional: Allows supervisor to pre-populate knowledge.
    """
    try:
        entry = knowledge_service.add_entry(entry_data)
        return entry
    except Exception as e:
        logger.error(f"Failed to create knowledge entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create entry")


@router.get("/{entry_id}", response_model=KnowledgeEntry)
async def get_knowledge_entry(entry_id: str):
    """Get a specific knowledge entry."""
    try:
        entry = knowledge_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get knowledge entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


@router.get("/summary/stats")
async def get_knowledge_summary():
    """Get summary statistics about knowledge base."""
    try:
        summary = knowledge_service.get_knowledge_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get knowledge summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get summary")
