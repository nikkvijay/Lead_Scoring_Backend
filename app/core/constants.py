"""Constants for the scoring engine and business logic"""

from typing import List


class ScoringConstants:
    """Scoring weights and thresholds"""

    # Rule-based scoring weights (max 50 points)
    MAX_RULE_SCORE = 50
    MAX_AI_SCORE = 50

    # Role scoring
    DECISION_MAKER_POINTS = 20
    INFLUENCER_POINTS = 10
    OTHER_ROLE_POINTS = 0

    # Industry scoring
    EXACT_INDUSTRY_POINTS = 20
    ADJACENT_INDUSTRY_POINTS = 10
    OTHER_INDUSTRY_POINTS = 0

    # Data completeness
    COMPLETE_DATA_POINTS = 10

    # AI scoring mapping
    AI_INTENT_SCORES = {
        "high": 50,
        "medium": 30,
        "low": 10
    }


class JobRoleCategories:
    """Job role classifications for scoring"""

    DECISION_MAKERS = [
        "ceo", "cto", "cfo", "coo", "founder", "co-founder",
        "president", "vp", "vice president", "director",
        "head of", "chief", "owner", "partner"
    ]

    INFLUENCERS = [
        "manager", "lead", "senior", "principal", "supervisor",
        "coordinator", "team lead", "specialist"
    ]


class IndustryMappings:
    """Industry categorization for related matching"""

    SAAS_RELATED = [
        "software", "saas", "technology", "tech", "it",
        "information technology", "software development"
    ]

    FINTECH_RELATED = [
        "fintech", "financial services", "banking", "finance",
        "payments", "cryptocurrency", "blockchain"
    ]

    ECOMMERCE_RELATED = [
        "ecommerce", "e-commerce", "retail", "marketplace",
        "online retail", "shopping"
    ]