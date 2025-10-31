"""
Unit tests for help request service.
"""
import pytest
from src.models.help_request import HelpRequestCreate, RequestStatus
from src.services.help_request_service import help_request_service


def test_create_help_request():
    """Test creating a help request."""
    request_data = HelpRequestCreate(
        customer_phone="+1234567890",
        customer_name="Test Customer",
        question="Do you have parking?",
        context="Planning to visit"
    )
    
    help_request = help_request_service.create_request(request_data)
    
    assert help_request.request_id is not None
    assert help_request.status == RequestStatus.PENDING
    assert help_request.customer_phone == "+1234567890"


def test_get_pending_requests():
    """Test retrieving pending requests."""
    pending = help_request_service.get_all_requests(RequestStatus.PENDING)
    
    assert isinstance(pending, list)