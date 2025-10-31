"""
Knowledge Base Service - Manages learned answers.
"""
from typing import List, Optional
from datetime import datetime
from src.models.knowledge_base import KnowledgeEntry, KnowledgeCreate
from src.models.help_request import HelpRequest
from src.database.firebase_client import firebase_client
from src.services.ai_service import ai_service
from src.utils.logger import logger


class KnowledgeService:
    """
    Manages the knowledge base that AI learns from.
    """
    
    def add_entry(self, entry_data: KnowledgeCreate) -> KnowledgeEntry:
        """Add a new entry to the knowledge base."""
        # Extract keywords if not provided
        if not entry_data.keywords:
            keywords = ai_service.extract_keywords(
                f"{entry_data.question} {entry_data.answer}"
            )
        else:
            keywords = entry_data.keywords
        
        entry = KnowledgeEntry(
            question=entry_data.question,
            answer=entry_data.answer,
            category=entry_data.category,
            keywords=keywords,
            source_request_id=entry_data.source_request_id
        )
        
        success = firebase_client.create_knowledge_entry(
            entry.entry_id,
            entry.to_dict()
        )
        
        if not success:
            logger.error("Failed to save knowledge entry")
            raise Exception("Database error")
        
        logger.info(f"Knowledge entry created: {entry.entry_id}")
        return entry
    
    def add_from_help_request(self, help_request: HelpRequest) -> KnowledgeEntry:
        """
        Automatically add knowledge from a resolved help request.
        """
        entry_data = KnowledgeCreate(
            question=help_request.question,
            answer=help_request.supervisor_answer,
            source_request_id=help_request.request_id
        )
        
        return self.add_entry(entry_data)
    
    def get_all_knowledge(self) -> List[KnowledgeEntry]:
        """Get all knowledge base entries."""
        data_list = firebase_client.get_all_knowledge()
        entries = [KnowledgeEntry.from_dict(data) for data in data_list]
        
        # Sort by most recently used
        entries.sort(
            key=lambda x: x.last_used_at or x.created_at, 
            reverse=True
        )
        
        return entries
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeEntry]:
        """
        Search knowledge base for relevant entries.
        
        Simple keyword-based search for Phase 1.
        Can be enhanced with vector similarity in Phase 2.
        """
        all_entries = self.get_all_knowledge()
        query_lower = query.lower()
        
        # Score entries based on keyword matches
        scored_entries = []
        for entry in all_entries:
            score = 0
            
            # Check question similarity
            if query_lower in entry.question.lower():
                score += 3
            
            # Check keywords
            for keyword in entry.keywords:
                if keyword.lower() in query_lower:
                    score += 1
            
            if score > 0:
                scored_entries.append((score, entry))
        
        # Sort by score and return top results
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored_entries[:limit]]
    
    def increment_usage(self, entry_id: str) -> bool:
        """Increment usage counter when knowledge is used."""
        entry = self.get_entry(entry_id)
        if not entry:
            return False
        
        now = datetime.utcnow()
        updates = {
            'times_used': entry.times_used + 1,
            'last_used_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        
        return firebase_client.update_knowledge_entry(entry_id, updates)
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get a specific knowledge entry."""
        data = firebase_client.get_knowledge_entry(entry_id)
        if data:
            return KnowledgeEntry.from_dict(data)
        return None
    
    def get_knowledge_summary(self) -> dict:
        """Get summary statistics about the knowledge base."""
        entries = self.get_all_knowledge()
        
        total_entries = len(entries)
        total_usage = sum(e.times_used for e in entries)
        
        # Category breakdown
        categories = {}
        for entry in entries:
            cat = entry.category or "uncategorized"
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_entries': total_entries,
            'total_usage': total_usage,
            'categories': categories,
            'most_used': sorted(entries, key=lambda x: x.times_used, reverse=True)[:5]
        }


# Global service instance
knowledge_service = KnowledgeService()