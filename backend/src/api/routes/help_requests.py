"""
Help Requests API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.models.help_request import (
    HelpRequest, HelpRequestCreate, RequestStatus
)
from src.services.help_request_service import help_request_service
from src.utils.logger import logger

router = APIRouter(redirect_slashes=False)  # Added this parameter


@router.post("/", response_model=HelpRequest, status_code=201)
async def create_help_request(request_data: HelpRequestCreate):
    """
    Create a new help request when AI doesn't know the answer.
    
    This is called by the AI agent when it needs human assistance.
    """
    try:
        help_request = help_request_service.create_request(request_data)
        return help_request
    except Exception as e:
        logger.error(f"Failed to create help request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create help request")


@router.get("/", response_model=List[HelpRequest])
async def get_help_requests(
    status: Optional[RequestStatus] = Query(None, description="Filter by status")
):
    """
    Get all help requests, optionally filtered by status.
    
    Used by supervisor UI to view pending requests.
    """
    try:
        requests = help_request_service.get_all_requests(status)
        return requests
    except Exception as e:
        logger.error(f"Failed to get help requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch help requests")


@router.get("/{request_id}", response_model=HelpRequest)
async def get_help_request(request_id: str):
    """Get a specific help request by ID."""
    try:
        help_request = help_request_service.get_request(request_id)
        if not help_request:
            raise HTTPException(status_code=404, detail="Help request not found")
        return help_request
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get help request: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


@router.post("/check-timeouts")
async def check_timeouts():
    """
    Manually trigger timeout check for old pending requests.
    
    Can be called by a cron job or scheduler.
    """
    try:
        count = help_request_service.check_and_timeout_old_requests()
        return {
            "message": f"Checked timeouts successfully",
            "timed_out_count": count
        }
    except Exception as e:
        logger.error(f"Failed to check timeouts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check timeouts")