import json
from app.config import settings
from app.intelligence.providers.base import BaseIntelligenceProvider, IntelligenceResult
from app.intelligence.providers.fallback import FallbackIntelligenceProvider
from app.intelligence.providers.gemini import GeminiIntelligenceProvider


def get_intelligence_provider() -> BaseIntelligenceProvider:
    """Factory function returning the configured intelligence provider with automatic fallback."""
    provider_name = settings.AI_PROVIDER.lower()

    if provider_name == "gemini" and settings.AI_API_KEY:
        return GeminiIntelligenceProvider()

    # Default to offline heuristic fallback
    return FallbackIntelligenceProvider()
