"""
Supervisor action routes.
"""
from fastapi import APIRouter, HTTPException
from src.models.help_request import HelpRequest, HelpRequestResolve, RequestStatus
from src.services.help_request_service import help_request_service
from src.utils.logger import logger

router = APIRouter()


@router.post("/{request_id}/resolve", response_model=HelpRequest)
async def resolve_help_request(
    request_id: str,
    resolution: HelpRequestResolve
):
    """
    Supervisor resolves a help request with an answer.
    
    This triggers:
    1. Update request to RESOLVED
    2. Notify customer
    3. Add to knowledge base
    """
    try:
        help_request = help_request_service.resolve_request(
            request_id, 
            resolution
        )
        
        if not help_request:
            raise HTTPException(
                status_code=404, 
                detail="Help request not found or already resolved"
            )
        
        return help_request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve help request: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to resolve help request"
        )


@router.get("/dashboard/stats")
async def get_supervisor_dashboard_stats():
    """
    Get statistics for supervisor dashboard.
    """
    try:
        from src.services.knowledge_service import knowledge_service
        
        all_requests = help_request_service.get_all_requests()
        pending = help_request_service.get_all_requests(RequestStatus.PENDING)
        
        knowledge_summary = knowledge_service.get_knowledge_summary()
        
        return {
            "total_requests": len(all_requests),
            "pending_requests": len(pending),
            "resolved_requests": len([
                r for r in all_requests 
                if r.status == RequestStatus.RESOLVED.value
            ]),
            "timed_out_requests": len([
                r for r in all_requests 
                if r.status == RequestStatus.TIMEOUT.value
            ]),
            "knowledge_entries": knowledge_summary['total_entries'],
            "knowledge_usage": knowledge_summary['total_usage']
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stats")