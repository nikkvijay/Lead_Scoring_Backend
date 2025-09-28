"""In-memory storage service for development/demo purposes"""

from typing import List, Optional
from app.models.lead import LeadModel, LeadScoringResult
from app.models.offer import OfferModel


class StorageService:
    """Simple in-memory storage for offers, leads, and results"""

    _offer: Optional[OfferModel] = None
    _leads: List[LeadModel] = []
    _results: List[LeadScoringResult] = []

    @classmethod
    def set_offer(cls, offer: OfferModel) -> None:
        """Store the current offer"""
        cls._offer = offer

    @classmethod
    def get_offer(cls) -> Optional[OfferModel]:
        """Retrieve the current offer"""
        return cls._offer

    @classmethod
    def set_leads(cls, leads: List[LeadModel]) -> None:
        """Store leads and clear previous results"""
        cls._leads = leads
        cls._results = []  # Clear results when new leads are uploaded

    @classmethod
    def get_leads(cls) -> List[LeadModel]:
        """Retrieve all stored leads"""
        return cls._leads

    @classmethod
    def set_results(cls, results: List[LeadScoringResult]) -> None:
        """Store scoring results"""
        cls._results = results

    @classmethod
    def get_results(cls) -> List[LeadScoringResult]:
        """Retrieve all scoring results"""
        return cls._results

    @classmethod
    def clear_all(cls) -> None:
        """Clear all stored data for testing"""
        cls._offer = None
        cls._leads = []
        cls._results = []