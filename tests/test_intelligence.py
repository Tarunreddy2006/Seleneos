import pytest
from app.intelligence.categorizer import RuleBasedCategorizer
from app.intelligence.providers.fallback import FallbackIntelligenceProvider
from app.intelligence.translator import OfflineGlossaryTranslator, FreeTranslationProvider
from app.intelligence.pipeline import IntelligencePipeline
from app.database.models import Article, Category


def test_rule_based_categorization():
    categorizer = RuleBasedCategorizer()

    # Economy test
    scores_econ = categorizer.classify("RBI lowers repo rate to spur capital investment and credit growth")
    assert len(scores_econ) > 0
    assert scores_econ[0][0] == "indian-economy"

    # Tech test
    scores_tech = categorizer.classify("ISRO launches quantum satellite with advanced artificial intelligence onboard")
    assert len(scores_tech) > 0
    assert scores_tech[0][0] == "technology-science"

    # Education test
    scores_edu = categorizer.classify("UGC introduces new curriculum framework for central universities and scholarships")
    assert len(scores_edu) > 0
    assert scores_edu[0][0] == "education"

    # Karnataka politics test
    scores_kar = categorizer.classify("Karnataka assembly passes state budget in Vidhana Soudha, Bengaluru")
    assert len(scores_kar) > 0
    assert scores_kar[0][0] == "karnataka-politics"


@pytest.mark.asyncio
async def test_fallback_intelligence_provider():
    provider = FallbackIntelligenceProvider()
    headline = "Government allocates ₹50,000 crore for semiconductor chip manufacturing"
    text = "The Union Cabinet approved the package on November 21, 2026. Growth is projected at 12.5% annually."

    result = await provider.analyze(headline, text, category_name="Technology & Science")
    assert result.summary != ""
    assert result.detailed_summary != ""
    assert "Technology & Science" in result.why_it_matters
    # Check facts extraction
    assert any("50,000" in f or "₹" in f for f in result.important_facts)
    assert any("12.5%" in f for f in result.important_facts)


@pytest.mark.asyncio
async def test_offline_translator_glossary():
    translator = OfflineGlossaryTranslator()
    text = "Reserve Bank of India announces new policy in Bengaluru"
    translated = await translator.translate_to_kannada(text)
    assert "ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ ಆಫ್ ಇಂಡಿಯಾ" in translated
    assert "ಬೆಂಗಳೂರು" in translated


@pytest.mark.asyncio
async def test_intelligence_pipeline_end_to_end(db_session):
    pipeline = IntelligencePipeline(db_session)

    article = Article(
        id="intel-test-1",
        headline="ISRO announces next generation launch vehicle program in Bengaluru",
        original_url="https://example.com/isro-nglv",
        publisher="National Science Wire",
        short_description="ISRO unveiled plans for heavy lift launch vehicle with ₹12,000 crore budget.",
        language="en"
    )
    db_session.add(article)
    db_session.commit()

    await pipeline.process_article(article)

    assert article.summary_en is not None
    assert article.why_it_matters_en is not None
    assert article.summary_kn is not None
    assert len(article.categories) >= 1
