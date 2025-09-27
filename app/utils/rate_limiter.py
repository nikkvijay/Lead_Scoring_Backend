"""Smart rate limiting for AI providers"""

import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SmartRateLimiter:
    """Smart rate limiter to prevent hitting API limits"""

    def __init__(self):
        self.calls = {"gemini": [], "openai": []}

    async def check_rate_limit(self, provider: str):
        """Prevent hitting rate limits with intelligent throttling"""
        now = datetime.now()
        calls = self.calls[provider]

        # Remove old calls (1 minute window)
        calls[:] = [call_time for call_time in calls if now - call_time < timedelta(minutes=1)]

        # Gemini: 15 requests/minute free tier, OpenAI: 500 requests/minute (tier 1)
        # Use conservative limits for safety margin
        max_calls = 10 if provider == "gemini" else 100

        if len(calls) >= max_calls:
            sleep_time = 60 - (now - calls[0]).seconds
            logger.info(f"Rate limit reached for {provider}, sleeping {sleep_time}s")
            await asyncio.sleep(sleep_time)

        calls.append(now)

    def get_remaining_calls(self, provider: str) -> int:
        """Get remaining calls in current window for monitoring"""
        now = datetime.now()
        calls = self.calls[provider]
        recent_calls = [call for call in calls if now - call < timedelta(minutes=1)]
        max_calls = 10 if provider == "gemini" else 100
        return max(0, max_calls - len(recent_calls))

    def reset_provider(self, provider: str):
        """Reset rate limit tracking for a provider"""
        self.calls[provider] = []