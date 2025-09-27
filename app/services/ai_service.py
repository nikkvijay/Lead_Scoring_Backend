"""Enhanced AI service with multi-provider fallback support"""

import asyncio
import logging
import json
import time
from typing import Tuple, List, Any

import openai
from openai import AsyncOpenAI
import google.generativeai as genai

from app.models.lead import LeadModel
from app.models.offer import OfferModel
from app.core.config import settings
from app.core.exceptions import AIServiceException
from app.utils.rate_limiter import SmartRateLimiter

logger = logging.getLogger(__name__)


class AIUsageTracker:
    """Track AI usage for cost monitoring and analytics"""

    _usage = {
        "gemini": {"calls": 0, "tokens": 0},
        "openai": {"calls": 0, "tokens": 0, "estimated_cost": 0.0},
        "failures": 0
    }

    @classmethod
    def log_usage(cls, provider: str, input_tokens: int, output_tokens: int = 50):
        """Log usage statistics for a provider"""
        cls._usage[provider]["calls"] += 1
        cls._usage[provider]["tokens"] += input_tokens + output_tokens

        if provider == "openai":
            # GPT-4o-mini pricing: ~$0.15/1M input tokens, $0.6/1M output
            cost = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)
            cls._usage["openai"]["estimated_cost"] += cost

    @classmethod
    def log_failure(cls):
        """Log a failure across all providers"""
        cls._usage["failures"] += 1

    @classmethod
    def get_stats(cls):
        """Get current usage statistics"""
        return cls._usage.copy()

    @classmethod
    def reset_stats(cls):
        """Reset usage statistics"""
        cls._usage = {
            "gemini": {"calls": 0, "tokens": 0},
            "openai": {"calls": 0, "tokens": 0, "estimated_cost": 0.0},
            "failures": 0
        }


class AIService:
    """Enhanced AI service with multi-provider fallback strategy"""

    def __init__(self):
        self.providers: List[Tuple[str, Any]] = []
        self.rate_limiter = SmartRateLimiter()
        self._setup_providers()

    def _setup_providers(self):
        """Setup AI providers based on configuration and availability"""
        # Primary: Gemini (free tier)
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel(settings.gemini_model)
                self.providers.append(("gemini", model))
                logger.info("Gemini provider configured successfully")
            except Exception as e:
                logger.warning(f"Failed to setup Gemini: {str(e)}")

        # Fallback: OpenAI
        if settings.openai_api_key:
            try:
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                self.providers.append(("openai", client))
                logger.info("OpenAI provider configured successfully")
            except Exception as e:
                logger.warning(f"Failed to setup OpenAI: {str(e)}")

        if not self.providers:
            raise AIServiceException("No AI providers configured successfully")

        logger.info(f"AI service initialized with {len(self.providers)} providers: {[p[0] for p in self.providers]}")

    async def analyze_lead_intent(self, lead: LeadModel, offer: OfferModel) -> Tuple[str, str]:
        """Analyze lead's buying intent using available AI providers with fallback"""
        last_error = None

        for provider_name, client in self.providers:
            try:
                logger.info(f"Attempting analysis with {provider_name} for lead: {lead.name}")
                start_time = time.time()

                # Check rate limits before making request
                await self.rate_limiter.check_rate_limit(provider_name)

                intent, reasoning = await self._analyze_with_provider(
                    provider_name, client, lead, offer
                )

                duration = time.time() - start_time
                logger.info(f"{provider_name} analysis completed in {duration:.2f}s for {lead.name}")

                return intent, reasoning

            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0
                logger.warning(f"{provider_name} failed after {duration:.2f}s: {str(e)}")
                last_error = e
                continue

        # All providers failed
        AIUsageTracker.log_failure()
        logger.error(f"All AI providers failed for {lead.name}. Last error: {last_error}")
        return "low", "AI services unavailable - conservative scoring applied"

    async def _analyze_with_provider(self, provider: str, client: Any, lead: LeadModel, offer: OfferModel) -> Tuple[str, str]:
        """Analyze lead intent with a specific provider"""
        prompt = self._build_analysis_prompt(lead, offer)

        try:
            if provider == "gemini":
                response = await asyncio.wait_for(
                    client.generate_content_async(prompt),
                    timeout=settings.ai_timeout
                )
                content = response.text.strip()
            elif provider == "openai":
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=200
                    ),
                    timeout=settings.ai_timeout
                )
                content = response.choices[0].message.content.strip()
            else:
                raise AIServiceException(f"Unsupported provider: {provider}")

            # Parse response and log usage
            intent, reasoning = self._parse_ai_response(content)
            AIUsageTracker.log_usage(provider, len(prompt), len(content))

            return intent, reasoning

        except asyncio.TimeoutError:
            raise AIServiceException(f"{provider} request timed out")
        except Exception as e:
            raise AIServiceException(f"{provider} error: {str(e)}", provider=provider)

    def _build_analysis_prompt(self, lead: LeadModel, offer: OfferModel) -> str:
        """Build cost-optimized prompt for AI analysis"""
        # Truncate bio for cost efficiency
        bio_truncated = lead.linkedin_bio[:200] if len(lead.linkedin_bio) > 200 else lead.linkedin_bio

        # Limit use cases for cost efficiency
        use_cases_limited = offer.ideal_use_cases[:2]

        return f"""Analyze buying intent: High/Medium/Low

Product: {offer.name}
Use cases: {', '.join(use_cases_limited)}

Prospect: {lead.name}, {lead.role} at {lead.company}
Industry: {lead.industry}
Bio: {bio_truncated}

JSON only: {{"intent": "High|Medium|Low", "reasoning": "Brief explanation"}}"""

    def _parse_ai_response(self, content: str) -> Tuple[str, str]:
        """Parse AI response and extract intent and reasoning"""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{') and content.strip().endswith('}'):
                data = json.loads(content)
                intent = data.get('intent', 'Low').lower()
                reasoning = data.get('reasoning', 'Analysis completed')
            else:
                # Fallback: text parsing
                intent, reasoning = self._parse_text_response(content)

            # Validate intent
            if intent not in ['high', 'medium', 'low']:
                logger.warning(f"Invalid intent '{intent}', defaulting to 'low'")
                intent = 'low'

            return intent, reasoning

        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}. Content: {content}")
            return 'low', 'Failed to parse AI analysis'

    def _parse_text_response(self, content: str) -> Tuple[str, str]:
        """Fallback text parsing for non-JSON responses"""
        content_lower = content.lower()

        # Extract intent
        if 'high' in content_lower:
            intent = 'high'
        elif 'medium' in content_lower:
            intent = 'medium'
        else:
            intent = 'low'

        # Use first sentence as reasoning
        sentences = content.split('.')
        reasoning = sentences[0].strip() if sentences else "AI analysis completed"

        return intent, reasoning