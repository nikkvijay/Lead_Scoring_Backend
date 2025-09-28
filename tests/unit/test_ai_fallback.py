"""Unit tests for AI fallback functionality"""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.ai_service import AIService, AIUsageTracker
from app.services.scoring_engine import ScoringEngine
from app.models.lead import LeadModel, IntentLevel
from app.models.offer import OfferModel
from app.core.exceptions import AIServiceException


class TestAIFallback:
    """Test AI service fallback mechanisms"""

    @pytest.fixture
    def sample_lead(self):
        return LeadModel(
            name="Test Lead",
            role="CEO",
            company="TestCorp",
            industry="software",
            location="SF",
            linkedin_bio="Test bio for analysis"
        )

    @pytest.fixture
    def sample_offer(self):
        return OfferModel(
            name="Test Product",
            value_props=["value1", "value2"],
            ideal_use_cases=["software", "technology"]
        )

    @pytest.mark.asyncio
    async def test_ai_fallback_mechanism(self, sample_lead, sample_offer, mocker):
        """Test that AI service falls back correctly when primary fails"""
        # Mock settings to have both providers
        mocker.patch('app.core.config.settings.gemini_api_key', "fake_key")
        mocker.patch('app.core.config.settings.openai_api_key', "fake_key")

        ai_service = AIService()

        # Mock the provider methods to simulate failure then success
        with patch.object(ai_service, '_analyze_with_provider') as mock_analyze:
            mock_analyze.side_effect = [
                AIServiceException("Gemini quota exceeded"),  # First call fails
                ("high", "Strong buying signals")              # Second call succeeds
            ]

            intent, reasoning = await ai_service.analyze_lead_intent(sample_lead, sample_offer)

            assert intent == "high"
            assert "Strong buying signals" in reasoning
            assert mock_analyze.call_count == 2  # Tried both providers

    @pytest.mark.asyncio
    async def test_all_providers_fail(self, sample_lead, sample_offer, mocker):
        """Test behavior when all AI providers fail"""
        mocker.patch('app.core.config.settings.gemini_api_key', "fake_key")
        mocker.patch('app.core.config.settings.openai_api_key', "fake_key")

        ai_service = AIService()

        with patch.object(ai_service, '_analyze_with_provider') as mock_analyze:
            mock_analyze.side_effect = AIServiceException("All providers failed")

            intent, reasoning = await ai_service.analyze_lead_intent(sample_lead, sample_offer)

            assert intent == "low"
            assert "conservative scoring applied" in reasoning

    def test_usage_tracker(self):
        """Test usage tracking functionality"""
        # Reset tracker
        AIUsageTracker.reset_stats()

        # Log some usage
        AIUsageTracker.log_usage("gemini", 100, 50)
        AIUsageTracker.log_usage("openai", 200, 75)

        stats = AIUsageTracker.get_stats()

        assert stats["gemini"]["calls"] == 1
        assert stats["gemini"]["tokens"] == 150
        assert stats["openai"]["calls"] == 1
        assert stats["openai"]["estimated_cost"] > 0

    def test_scoring_engine_rule_logic(self, sample_lead, sample_offer):
        """Test rule-based scoring logic"""
        scoring_engine = ScoringEngine()

        # Test high-scoring lead
        high_score_lead = LeadModel(
            name="John CEO",
            role="CEO",  # Decision maker: 20 points
            company="TechCorp",
            industry="software",  # Exact match: 20 points
            location="SF",
            linkedin_bio="Complete bio"  # Complete: 10 points
        )

        rule_score, breakdown = scoring_engine._calculate_rule_score(high_score_lead, sample_offer)

        assert rule_score == 50  # Maximum rule score
        assert "Role: 20pts" in breakdown
        assert "Industry: 20pts" in breakdown
        assert "Completeness: 10pts" in breakdown