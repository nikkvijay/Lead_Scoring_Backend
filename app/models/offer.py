"""Offer data models and validation"""

from pydantic import BaseModel, Field, validator
from typing import List


class OfferModel(BaseModel):
    """Model for product/offer data with validation"""

    name: str = Field(..., min_length=1, max_length=200, description="Product/service name")
    value_props: List[str] = Field(..., min_items=1, max_items=10, description="Key value propositions")
    ideal_use_cases: List[str] = Field(..., min_items=1, max_items=10, description="Target use cases/industries")

    @validator('value_props', 'ideal_use_cases', pre=True)
    def clean_lists(cls, v):
        """Clean and validate list fields"""
        if isinstance(v, list):
            return [item.strip() for item in v if item and item.strip()]
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "AI Outreach Automation",
                "value_props": [
                    "24/7 automated outreach",
                    "6x more qualified meetings",
                    "AI-powered personalization"
                ],
                "ideal_use_cases": [
                    "B2B SaaS companies",
                    "Mid-market technology companies"
                ]
            }
        }