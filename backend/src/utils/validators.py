"""
Input validation utilities.
"""
import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
    
    Returns:
        True if valid, False otherwise
    """
    # Simple validation - accepts formats like +1234567890, 1234567890, etc.
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


def sanitize_phone_for_key(phone: str) -> str:
    """
    Sanitize phone number for use as Firebase key.
    
    Args:
        phone: Phone number
    
    Returns:
        Sanitized phone string
    """
    return phone.replace('+', '_').replace(' ', '').replace('-', '')


def validate_text_length(text: str, min_length: int = 1, max_length: int = 1000) -> bool:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
    
    Returns:
        True if valid, False otherwise
    """
    return min_length <= len(text) <= max_length