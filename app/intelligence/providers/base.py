from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IntelligenceResult:
    def __init__(
        self,
        summary: str,
        detailed_summary: str,
        why_it_matters: str,
        important_facts: List[str],
        background: Optional[str] = None
    ):
        self.summary = summary
        self.detailed_summary = detailed_summary
        self.why_it_matters = why_it_matters
        self.important_facts = important_facts
        self.background = background

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "detailed_summary": self.detailed_summary,
            "why_it_matters": self.why_it_matters,
            "important_facts": self.important_facts,
            "background": self.background
        }


class BaseIntelligenceProvider(ABC):
    """Abstract interface for AI and rule-based intelligence synthesis."""

    @abstractmethod
    async def analyze(self, headline: str, text: str, category_name: str = "") -> IntelligenceResult:
        """Generates concise summary, detailed explanation, why it matters, and key facts."""
        pass
