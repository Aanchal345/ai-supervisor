"""
Custom exceptions for the application.
"""


class AIServiceError(Exception):
    """Raised when AI service fails."""
    pass


class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass


class HelpRequestNotFoundError(Exception):
    """Raised when help request is not found."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass