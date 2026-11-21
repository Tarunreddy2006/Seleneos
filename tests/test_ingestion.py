import pytest
import datetime
from unittest.mock import AsyncMock, patch
import httpx

from app.ingestion.normalizer import canonicalize_url, clean_html_text, generate_content_hash
from app.ingestion.rss_parser import parse_rss_feed
from app.ingestion.deduplicator import Deduplicator, calculate_jaccard_similarity
from app.ingestion.collector import NewsCollector
from app.database.models import Source, Category, Article

SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Sample News Channel</title>
    <link>https://example.com/news</link>
    <description>Daily intelligence sample feed</description>
    <item>
      <title><![CDATA[RBI Keeps Repo Rate Unchanged at 6.5%]]></title>
      <link>https://example.com/news/rbi-rate-decision?utm_source=twitter&amp;utm_campaign=breaking#top</link>
      <description><![CDATA[<p>The Reserve Bank of India Monetary Policy Committee has decided to keep the repo rate unchanged.</p>]]></description>
      <pubDate>Fri, 21 Nov 2026 04:30:00 GMT</pubDate>
      <media:content url="https://example.com/images/rbi.jpg" medium="image" />
    </item>
    <item>
      <title>ISRO Launches Advanced Meteorological Satellite</title>
      <link>https://example.com/news/isro-launch/?ref=rss</link>
      <description>ISRO has successfully placed the satellite into geostationary transfer orbit.</description>
      <pubDate>Fri, 21 Nov 2026 05:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


def test_url_canonicalization():
    raw_url = "HTTPS://Example.COM:443/news/article/?utm_source=news&utm_medium=email&id=123#comments"
    canonical = canonicalize_url(raw_url)
    assert canonical == "https://example.com/news/article?id=123"

    raw_trailing = "https://example.com/path/"
    assert canonicalize_url(raw_trailing) == "https://example.com/path"


def test_clean_html_text():
    dirty_html = "<div><p>Breaking: <b>Tech breakthrough</b></p><script>alert('xss');</script><style>.bad{}</style></div>"
    clean = clean_html_text(dirty_html)
    assert clean == "Breaking: Tech breakthrough"
    assert "alert" not in clean
    assert ".bad" not in clean


def test_parse_rss_feed():
    articles = parse_rss_feed(SAMPLE_RSS_XML, source_name="Sample Wire", default_language="en")
    assert len(articles) == 2

    a1 = articles[0]
    assert a1.headline == "RBI Keeps Repo Rate Unchanged at 6.5%"
    assert a1.canonical_url == "https://example.com/news/rbi-rate-decision"
    assert a1.publisher == "Sample Wire"
    assert a1.thumbnail_url == "https://example.com/images/rbi.jpg"
    assert "Monetary Policy Committee" in a1.short_description

    a2 = articles[1]
    assert a2.headline == "ISRO Launches Advanced Meteorological Satellite"
    assert a2.canonical_url == "https://example.com/news/isro-launch"


def test_deduplicator_similarity_and_exact():
    dedup = Deduplicator()

    # Exact duplicate test
    title1 = "RBI Holds Benchmark Interest Rate Steady at 6.5%"
    title2 = "RBI Keeps Benchmark Interest Rate Steady at 6.5%"
    title3 = "NASA Discovers Habitable Exoplanet in Trappist System"

    sim_high = calculate_jaccard_similarity(title1, title2)
    sim_low = calculate_jaccard_similarity(title1, title3)

    assert sim_high >= 0.60
    assert sim_low < 0.20


@pytest.mark.asyncio
async def test_collector_run(db_session):
    # Setup test source
    cat = db_session.query(Category).filter_by(id="indian-economy").first()
    source = Source(
        id="test-rbi-wire",
        name="Test RBI Wire",
        feed_url="https://example.com/mock-feed.xml",
        default_category_id=cat.id if cat else None,
        language="en",
        is_enabled=True
    )
    db_session.add(source)
    db_session.commit()

    collector = NewsCollector(db_session)

    # Mock HTTP response
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_RSS_XML

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        run = await collector.run_collection(trigger_type="test")
        assert run.status == "completed"
        assert run.sources_succeeded >= 1
        assert run.articles_added >= 2

    # Verify duplicate avoidance on second run
    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        run2 = await collector.run_collection(trigger_type="test")
        assert run2.articles_added == 0
        assert run2.articles_deduplicated >= 2
