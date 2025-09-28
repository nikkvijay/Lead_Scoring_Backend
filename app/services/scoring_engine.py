"""Core scoring engine with rule-based logic and AI integration"""

import asyncio
import logging
from typing import List, Tuple
from datetime import datetime

from app.models.lead import LeadModel, LeadScoringResult, IntentLevel
from app.models.offer import OfferModel
from app.core.constants import ScoringConstants, JobRoleCategories, IndustryMappings

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Hybrid scoring engine combining rule-based logic with AI analysis"""

    def __init__(self):
        # AI service will be injected to avoid circular imports
        self.ai_service = None

    def set_ai_service(self, ai_service):
        """Inject AI service dependency for testability"""
        self.ai_service = ai_service

    async def score_leads(self, leads: List[LeadModel], offer: OfferModel) -> List[LeadScoringResult]:
        """Score multiple leads against an offer with intelligent batching"""
        start_time = datetime.utcnow()

        logger.info(f"Starting to score {len(leads)} leads against offer: {offer.name}")

        # Process leads in batches to avoid overwhelming AI service
        batch_size = 10
        results = []

        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]
            batch_results = await self._score_batch(batch, offer)
            results.extend(batch_results)

            # Small delay between batches to be respectful to AI API
            if i + batch_size < len(leads):
                await asyncio.sleep(0.1)

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Completed scoring {len(leads)} leads in {duration:.2f} seconds")

        return results

    async def _score_batch(self, leads: List[LeadModel], offer: OfferModel) -> List[LeadScoringResult]:
        """Score a batch of leads concurrently for performance"""
        tasks = [self.score_single_lead(lead, offer) for lead in leads]
        return await asyncio.gather(*tasks)

    async def score_single_lead(self, lead: LeadModel, offer: OfferModel) -> LeadScoringResult:
        """Score a single lead against an offer using hybrid approach"""
        start_time = datetime.utcnow()

        # Calculate rule-based score (transparent and fast)
        rule_score, rule_breakdown = self._calculate_rule_score(lead, offer)

        # Get AI score (intelligent but may fail)
        ai_score, ai_reasoning, intent = await self._calculate_ai_score(lead, offer)

        # Calculate total score
        total_score = min(rule_score + ai_score, 100)

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.debug(f"Scored {lead.name} in {processing_time:.2f}ms: {total_score} points")

        return LeadScoringResult(
            name=lead.name,
            role=lead.role,
            company=lead.company,
            intent=IntentLevel(intent.title()),  # Ensure proper capitalization
            score=total_score,
            reasoning=f"Rule: {rule_breakdown}. AI: {ai_reasoning}"
        )

    def _calculate_rule_score(self, lead: LeadModel, offer: OfferModel) -> Tuple[int, str]:
        """Calculate rule-based score (max 50 points) with transparent logic"""
        score = 0
        breakdown_parts = []

        # Role relevance (max 20 points)
        role_score = self._score_role(lead.role)
        score += role_score
        breakdown_parts.append(f"Role: {role_score}pts")

        # Industry match (max 20 points)
        industry_score = self._score_industry(lead.industry, offer.ideal_use_cases)
        score += industry_score
        breakdown_parts.append(f"Industry: {industry_score}pts")

        # Data completeness (max 10 points)
        completeness_score = self._score_completeness(lead)
        score += completeness_score
        breakdown_parts.append(f"Completeness: {completeness_score}pts")

        breakdown = " | ".join(breakdown_parts)
        return min(score, ScoringConstants.MAX_RULE_SCORE), breakdown

    def _score_role(self, role: str) -> int:
        """Score based on job role decision-making power"""
        role_lower = role.lower()

        # Check for decision maker roles (highest priority)
        for decision_role in JobRoleCategories.DECISION_MAKERS:
            if decision_role in role_lower:
                return ScoringConstants.DECISION_MAKER_POINTS

        # Check for influencer roles (medium priority)
        for influencer_role in JobRoleCategories.INFLUENCERS:
            if influencer_role in role_lower:
                return ScoringConstants.INFLUENCER_POINTS

        return ScoringConstants.OTHER_ROLE_POINTS

    def _score_industry(self, lead_industry: str, target_industries: List[str]) -> int:
        """Score based on industry match with fuzzy matching"""
        lead_industry_lower = lead_industry.lower()
        target_industries_lower = [industry.lower() for industry in target_industries]

        # Exact match (highest score)
        if lead_industry_lower in target_industries_lower:
            return ScoringConstants.EXACT_INDUSTRY_POINTS

        # Fuzzy matching for related industries
        for target in target_industries_lower:
            if self._industries_related(lead_industry_lower, target):
                return ScoringConstants.ADJACENT_INDUSTRY_POINTS

        return ScoringConstants.OTHER_INDUSTRY_POINTS

    def _industries_related(self, lead_industry: str, target_industry: str) -> bool:
        """Check if industries are related using predefined mappings"""
        # SaaS/Tech related matching
        if any(term in lead_industry for term in IndustryMappings.SAAS_RELATED) and \
           any(term in target_industry for term in IndustryMappings.SAAS_RELATED):
            return True

        # Fintech related matching
        if any(term in lead_industry for term in IndustryMappings.FINTECH_RELATED) and \
           any(term in target_industry for term in IndustryMappings.FINTECH_RELATED):
            return True

        # E-commerce related matching
        if any(term in lead_industry for term in IndustryMappings.ECOMMERCE_RELATED) and \
           any(term in target_industry for term in IndustryMappings.ECOMMERCE_RELATED):
            return True

        return False

    def _score_completeness(self, lead: LeadModel) -> int:
        """Score based on data completeness"""
        required_fields = [
            lead.name, lead.role, lead.company,
            lead.industry, lead.location, lead.linkedin_bio
        ]

        if all(field and field.strip() for field in required_fields):
            return ScoringConstants.COMPLETE_DATA_POINTS

        return 0

    async def _calculate_ai_score(self, lead: LeadModel, offer: OfferModel) -> Tuple[int, str, str]:
        """Calculate AI-based score with comprehensive fallback handling"""
        if not self.ai_service:
            # Fallback when AI service is not available
            logger.warning("AI service not configured, using conservative scoring")
            return 10, "AI service unavailable - conservative scoring applied", "low"

        try:
            intent, reasoning = await self.ai_service.analyze_lead_intent(lead, offer)
            score = ScoringConstants.AI_INTENT_SCORES.get(intent.lower(), 10)
            return score, reasoning, intent

        except Exception as e:
            logger.error(f"AI scoring failed for lead {lead.name}: {str(e)}")
            # Fallback to conservative scoring when AI fails
            return 10, "AI analysis failed - conservative scoring applied", "low"