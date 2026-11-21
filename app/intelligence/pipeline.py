import json
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.database.models import Article, Category
from app.intelligence.categorizer import RuleBasedCategorizer
from app.intelligence.providers import get_intelligence_provider
from app.intelligence.translator import FreeTranslationProvider


class IntelligencePipeline:
    """
    Coordinates Article Classification, Summarization, and Translation.
    COLLECTION ──► CLASSIFICATION ──► SUMMARIZATION ──► TRANSLATION ──► STORAGE
    """

    def __init__(self, db: Session):
        self.db = db
        self.categorizer = RuleBasedCategorizer()
        self.ai_provider = get_intelligence_provider()
        self.translator = FreeTranslationProvider()

    async def process_article(self, article: Article) -> None:
        """Processes a single article through categorization, summarization, and translation."""
        # 1. Classification
        category_scores = self.categorizer.classify(article.headline, article.short_description or "")
        primary_category_name = ""

        if category_scores:
            # Associate up to top 2 relevant categories
            category_map = {c.id: c for c in self.db.query(Category).all()}
            for i, (cat_id, score) in enumerate(category_scores[:2]):
                cat = category_map.get(cat_id)
                if cat and cat not in article.categories:
                    article.categories.append(cat)
                    if i == 0:
                        primary_category_name = cat.name_en
        elif article.source and article.source.default_category:
            if article.source.default_category not in article.categories:
                article.categories.append(article.source.default_category)
                primary_category_name = article.source.default_category.name_en

        # 2. English Summarization
        intel_result = await self.ai_provider.analyze(
            headline=article.headline,
            text=article.short_description or article.headline,
            category_name=primary_category_name
        )

        article.summary_en = intel_result.summary
        article.detailed_summary_en = intel_result.detailed_summary
        article.why_it_matters_en = intel_result.why_it_matters
        article.background_en = intel_result.background
        article.important_facts = json.dumps(intel_result.important_facts)

        # 3. Kannada Translation (with entity preservation & English fallback)
        try:
            article.summary_kn = await self.translator.translate_to_kannada(intel_result.summary)
            article.detailed_summary_kn = await self.translator.translate_to_kannada(intel_result.detailed_summary)
            article.why_it_matters_kn = await self.translator.translate_to_kannada(intel_result.why_it_matters)
            if intel_result.background:
                article.background_kn = await self.translator.translate_to_kannada(intel_result.background)
        except Exception as exc:
            logger.warning("Translation failed for article %s: %s. Preserving English.", article.id, exc)
            article.summary_kn = article.summary_en
            article.detailed_summary_kn = article.detailed_summary_en
            article.why_it_matters_kn = article.why_it_matters_en

        self.db.flush()

    async def process_batch(self, limit: int = 25) -> int:
        """Processes unprocessed articles in the database."""
        unprocessed = self.db.query(Article).filter(
            (Article.summary_en == None) | (Article.summary_en == "")
        ).limit(limit).all()

        count = 0
        for art in unprocessed:
            await self.process_article(art)
            count += 1

        self.db.commit()
        return count
