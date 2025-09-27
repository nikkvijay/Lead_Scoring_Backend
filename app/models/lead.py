"""Lead data models and validation"""

from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional


class IntentLevel(str, Enum):
    """Lead buying intent classification"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class LeadModel(BaseModel):
    """Model for lead data with validation"""

    name: str = Field(..., min_length=1, max_length=100, description="Lead's full name")
    role: str = Field(..., min_length=1, max_length=100, description="Job role/title")
    company: str = Field(..., min_length=1, max_length=100, description="Company name")
    industry: str = Field(..., min_length=1, max_length=100, description="Industry sector")
    location: str = Field(..., min_length=1, max_length=100, description="Geographic location")
    linkedin_bio: str = Field(..., max_length=1000, description="LinkedIn bio/summary")

    @validator('*', pre=True)
    def strip_strings(cls, v):
        """Remove whitespace from all string fields"""
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ava Patel",
                "role": "Head of Growth",
                "company": "FlowMetrics",
                "industry": "software",
                "location": "San Francisco",
                "linkedin_bio": "Leading growth at a fast-growing B2B SaaS startup. Focused on scaling outreach operations and improving conversion rates."
            }
        }


class LeadScoringResult(BaseModel):
    """Model for lead scoring results"""

    name: str
    role: str
    company: str
    intent: IntentLevel
    score: int = Field(..., ge=0, le=100, description="Total score (0-100)")
    reasoning: str = Field(..., description="Explanation of scoring decision")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ava Patel",
                "role": "Head of Growth",
                "company": "FlowMetrics",
                "intent": "High",
                "score": 85,
                "reasoning": "Rule: Role: 20pts | Industry: 20pts | Completeness: 10pts. AI: Perfect ICP match with decision-maker role in target industry"
            }
        }