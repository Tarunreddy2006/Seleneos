import json
import httpx
from app.config import settings
from app.core.logging import logger
from app.intelligence.providers.base import BaseIntelligenceProvider, IntelligenceResult
from app.intelligence.providers.fallback import FallbackIntelligenceProvider


class GeminiIntelligenceProvider(BaseIntelligenceProvider):
    """
    Gemini API Intelligence Provider.
    Extracts structured editorial synthesis using Gemini 2.5 Flash.
    Falls back gracefully to FallbackIntelligenceProvider on any API error or timeout.
    """

    def __init__(self):
        self.fallback = FallbackIntelligenceProvider()
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL_NAME or "gemini-2.5-flash"

    async def analyze(self, headline: str, text: str, category_name: str = "") -> IntelligenceResult:
        if not self.api_key:
            return await self.fallback.analyze(headline, text, category_name)

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        prompt = f"""You are a senior intelligence analyst. Analyze this news article:
Category: {category_name}
Headline: {headline}
Content: {text}

Respond strictly with valid JSON conforming to this schema:
{{
  "summary": "1-2 sentence concise factual summary preserving names and figures",
  "detailed_summary": "Comprehensive 3-4 sentence detailed explanation of the development",
  "why_it_matters": "2-3 sentences explaining the strategic, economic, or policy impact",
  "important_facts": ["list of key numbers, dates, or confirmed facts"],
  "background": "Brief historical or institutional context explaining how we arrived here"
}}"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidate = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(candidate)
                    return IntelligenceResult(
                        summary=parsed.get("summary", ""),
                        detailed_summary=parsed.get("detailed_summary", ""),
                        why_it_matters=parsed.get("why_it_matters", ""),
                        important_facts=parsed.get("important_facts", []),
                        background=parsed.get("background", "")
                    )
                else:
                    logger.warning("Gemini API error (HTTP %d): %s. Using fallback.", resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Gemini API call failed (%s). Using fallback.", exc)

        return await self.fallback.analyze(headline, text, category_name)
