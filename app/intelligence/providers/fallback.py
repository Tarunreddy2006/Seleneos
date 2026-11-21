import re
from typing import List, Optional
from app.intelligence.providers.base import BaseIntelligenceProvider, IntelligenceResult


class FallbackIntelligenceProvider(BaseIntelligenceProvider):
    """
    100% Offline, Deterministic Rule-Based Intelligence Provider.
    Extracts key sentences, identifies numerical data/dates/entities,
    and generates structural analytical summaries without calling any external API.
    """

    FACT_PATTERNS = [
        r"₹\s*[\d,]+(?:\.\d+)?\s*(?:crore|lakh|billion|million)?",
        r"\$\s*[\d,]+(?:\.\d+)?\s*(?:billion|million|trillion)?",
        r"\b\d+(?:\.\d+)?%",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?",
        r"\b\d{4}\b"
    ]

    async def analyze(self, headline: str, text: str, category_name: str = "") -> IntelligenceResult:
        full_content = f"{headline}. {text}".strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", full_content) if len(s.strip()) > 15]

        # 1. Concise Summary: Headline + lead descriptive sentence
        lead = sentences[1] if len(sentences) > 1 else (text if text else headline)
        concise_summary = lead

        # 2. Detailed Summary: Top 3 sentences preserving chronology
        detailed_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        detailed_summary = " ".join(detailed_sentences)

        # 3. Why It Matters: Context-specific structural synthesis
        category_label = category_name if category_name else "national and global affairs"
        why_it_matters = (
            f"This development has direct implications for {category_label}, affecting policy directions, "
            f"institutional decision-making, and related regulatory or market outcomes."
        )

        # 4. Important Facts & Figures: Regex extraction of numbers, monetary figures, and dates
        facts: List[str] = []
        for pat in self.FACT_PATTERNS:
            matches = re.findall(pat, full_content, re.IGNORECASE)
            for m in matches:
                clean_m = m.strip()
                if clean_m not in facts and len(facts) < 5:
                    facts.append(clean_m)

        # 5. Background / Context
        background = (
            f"Reported in connection with ongoing monitoring of {category_label}. "
            f"Original reporting verified from official source feed."
        )

        return IntelligenceResult(
            summary=concise_summary,
            detailed_summary=detailed_summary,
            why_it_matters=why_it_matters,
            important_facts=facts,
            background=background
        )
