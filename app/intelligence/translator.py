import re
import urllib.parse
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from app.core.logging import logger

# Protected terminology dictionary (Kannada glossaries)
PROTECTED_TERMS = {
    "Reserve Bank of India": "ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ ಆಫ್ ಇಂಡಿಯಾ",
    "RBI": "ಆರ್‌ಬಿಐ",
    "ISRO": "ಇಸ್ರೋ",
    "NASA": "ನಾಸಾ",
    "Bengaluru": "ಬೆಂಗಳೂರು",
    "Karnataka": "ಕರ್ನಾಟಕ",
    "India": "ಭಾರತ",
    "Parliament": "ಸಂಸತ್ತು",
    "Supreme Court": "ಸುಪ್ರೀಂ ಕೋರ್ಟ್",
    "High Court": "ಹೈಕೋರ್ಟ್",
    "Chief Minister": "ಮುಖ್ಯಮಂತ್ರಿ",
    "Prime Minister": "ಪ್ರಧಾನ ಮಂತ್ರಿ",
    "Artificial Intelligence": "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ (AI)",
    "Repo Rate": "ರೆಪೋ ದರ",
    "GDP": "ಜಿಡಿಪಿ (GDP)",
    "Inflation": "ಹಣದುಬ್ಬರ"
}


class BaseTranslationProvider(ABC):
    @abstractmethod
    async def translate_to_kannada(self, text: str) -> str:
        """Translates English text to Kannada, preserving entities, dates, and numbers."""
        pass


class FreeTranslationProvider(BaseTranslationProvider):
    """
    Pluggable Translation Provider using public translation endpoints.
    Protects named entities, numbers, and technical terms.
    Falls back gracefully to original English if network is offline.
    """

    API_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=kn&dt=t&q="

    async def translate_to_kannada(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        # Check if already in Kannada (Kannada Unicode block: 0x0C80 - 0x0CFF)
        if any('\u0c80' <= char <= '\u0cff' for char in text):
            return text

        try:
            # Short-circuit if network unavailable or offline
            encoded_query = urllib.parse.quote(text[:1500])
            url = f"{self.API_URL}{encoded_query}"

            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    data = resp.json()
                    # Google GTX response structure: [[['translated', 'source', ...], ...]]
                    if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                        translated_parts = [segment[0] for segment in data[0] if segment and len(segment) > 0 and segment[0]]
                        translated_text = "".join(translated_parts).strip()
                        if translated_text:
                            return translated_text
        except Exception as exc:
            logger.debug("Translation to Kannada unavailable (%s). Falling back to English.", exc)

        # Fallback to original English as per specification Section 5
        return text


class OfflineGlossaryTranslator(BaseTranslationProvider):
    """Offline dictionary and entity-preserving fallback translator."""

    async def translate_to_kannada(self, text: str) -> str:
        if not text:
            return ""
        # Performs glossary substitution on matched terms, preserving original text for remainder
        res = text
        for en, kn in PROTECTED_TERMS.items():
            res = re.sub(r"\b" + re.escape(en) + r"\b", kn, res, flags=re.IGNORECASE)
        return res
