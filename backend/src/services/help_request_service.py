"""
Help Request Service - Business logic for managing help requests.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from src.models.help_request import (
    HelpRequest, HelpRequestCreate, HelpRequestResolve, RequestStatus
)
from src.database.firebase_client import firebase_client
from src.services.notification_service import notification_service
from src.services.knowledge_service import knowledge_service
from src.config.settings import settings
from src.utils.logger import logger


class HelpRequestService:
    """
    Manages the lifecycle of help requests.
    """
    
    def create_request(self, request_data: HelpRequestCreate) -> HelpRequest:
        """
        Create a new help request and notify supervisor.
        """
        # Calculate timeout
        timeout_at = datetime.utcnow() + timedelta(
            seconds=settings.help_request_timeout
        )
        
        # Create request object
        help_request = HelpRequest(
            customer_phone=request_data.customer_phone,
            customer_name=request_data.customer_name,
            question=request_data.question,
            context=request_data.context,
            timeout_at=timeout_at
        )
        
        # Save to database
        success = firebase_client.create_help_request(
            help_request.request_id,
            help_request.to_dict()
        )
        
        if not success:
            logger.error("Failed to save help request to database")
            raise Exception("Database error")
        
        # Notify supervisor
        notification_service.notify_supervisor(help_request)
        
        logger.info(f"Help request created: {help_request.request_id}")
        return help_request
    
    def get_request(self, request_id: str) -> Optional[HelpRequest]:
        """Get a specific help request."""
        data = firebase_client.get_help_request(request_id)
        if data:
            return HelpRequest.from_dict(data)
        return None
    
    def get_all_requests(
        self, 
        status: Optional[RequestStatus] = None
    ) -> List[HelpRequest]:
        """Get all help requests, optionally filtered by status."""
        status_str = status.value if status else None
        data_list = firebase_client.get_all_help_requests(status_str)
        
        requests = [HelpRequest.from_dict(data) for data in data_list]
        
        # Sort by creation time (newest first)
        requests.sort(key=lambda x: x.created_at, reverse=True)
        
        return requests
    
    def resolve_request(
        self, 
        request_id: str, 
        resolution: HelpRequestResolve
    ) -> Optional[HelpRequest]:
        """
        Resolve a help request with supervisor's answer.
        
        This triggers:
        1. Update request status to RESOLVED
        2. Notify customer with the answer
        3. Add answer to knowledge base
        """
        # Get existing request
        help_request = self.get_request(request_id)
        if not help_request:
            logger.error(f"Request not found: {request_id}")
            return None
        
        if help_request.status != RequestStatus.PENDING:
            logger.warning(f"Request {request_id} is not pending")
            return help_request
        
        # Update request
        now = datetime.utcnow()
        updates = {
            'status': RequestStatus.RESOLVED.value,
            'supervisor_answer': resolution.supervisor_answer,
            'supervisor_id': resolution.supervisor_id,
            'resolved_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        
        success = firebase_client.update_help_request(request_id, updates)
        if not success:
            logger.error("Failed to update help request")
            return None
        
        # Update local object
        help_request.status = RequestStatus.RESOLVED
        help_request.supervisor_answer = resolution.supervisor_answer
        help_request.supervisor_id = resolution.supervisor_id
        help_request.resolved_at = now
        help_request.updated_at = now
        
        # Notify customer
        notification_success = notification_service.notify_customer(
            help_request.customer_phone,
            help_request.question,
            resolution.supervisor_answer
        )
        
        if notification_success:
            firebase_client.update_help_request(request_id, {
                'customer_notified': True,
                'notification_sent_at': now.isoformat()
            })
            help_request.customer_notified = True
            help_request.notification_sent_at = now
        
        # Add to knowledge base
        knowledge_service.add_from_help_request(help_request)
        
        logger.info(f"Request resolved: {request_id}")
        return help_request
    
    def mark_timeout(self, request_id: str) -> bool:
        """Mark a request as timed out."""
        now = datetime.utcnow()
        updates = {
            'status': RequestStatus.TIMEOUT.value,
            'updated_at': now.isoformat()
        }
        
        success = firebase_client.update_help_request(request_id, updates)
        
        if success:
            logger.info(f"Request timed out: {request_id}")
        
        return success
    
    def check_and_timeout_old_requests(self) -> int:
        """
        Check for requests that have exceeded timeout and mark them.
        
        Returns:
            Number of requests timed out
        """
        pending_requests = self.get_all_requests(RequestStatus.PENDING)
        now = datetime.utcnow()
        timed_out_count = 0
        
        for request in pending_requests:
            if request.timeout_at and now > request.timeout_at:
                if self.mark_timeout(request.request_id):
                    timed_out_count += 1
        
        if timed_out_count > 0:
            logger.info(f"Timed out {timed_out_count} requests")
        
        return timed_out_count


# Global service instance
help_request_service = HelpRequestService()