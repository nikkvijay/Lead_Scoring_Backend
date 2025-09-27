"""Custom exceptions for the Lead Scoring API"""


class LeadScoringException(Exception):
    """Base exception for lead scoring related errors"""
    pass


class AIServiceException(LeadScoringException):
    """Exception raised when AI service operations fail"""

    def __init__(self, message: str, provider: str = None, cost_estimate: float = None):
        self.provider = provider
        self.cost_estimate = cost_estimate
        super().__init__(message)


class CSVProcessingException(LeadScoringException):
    """Exception raised when CSV processing fails"""
    pass


class ValidationException(LeadScoringException):
    """Exception raised when data validation fails"""
    pass