import datetime
import uuid
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.session import Base


# Many-to-many association between Articles and Categories
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", String(64), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", String(32), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    Column("is_primary", Boolean, default=False, nullable=False),
    Column("relevance_score", Float, default=1.0, nullable=False)
)

# Many-to-many association between Articles and Educational Topics
article_topics = Table(
    "article_topics",
    Base.metadata,
    Column("article_id", String(64), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", String(64), ForeignKey("educational_topics.id", ondelete="CASCADE"), primary_key=True)
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(32), primary_key=True)  # e.g. "global-business", "indian-economy"
    name_en = Column(String(100), nullable=False)
    name_kn = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    articles = relationship("Article", secondary=article_categories, back_populates="categories")
    sources = relationship("Source", back_populates="default_category")
    educational_topics = relationship("EducationalTopic", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.id}: {self.name_en}>"


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(64), primary_key=True)  # e.g. "the-hindu-national"
    name = Column(String(128), nullable=False)
    feed_url = Column(String(512), nullable=False, unique=True, index=True)
    site_url = Column(String(512), nullable=True)
    default_category_id = Column(String(32), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    language = Column(String(10), default="en", nullable=False)
    source_type = Column(String(32), default="rss", nullable=False)  # rss, api, press_release
    is_enabled = Column(Boolean, default=True, nullable=False)
    fetch_interval_minutes = Column(Integer, default=360, nullable=False)

    # Health and operational metrics
    last_collected_at = Column(DateTime, nullable=True)
    last_status = Column(String(32), default="never_run", nullable=False)  # success, error, timeout
    last_error_message = Column(Text, nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    total_articles_collected = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    default_category = relationship("Category", back_populates="sources")
    articles = relationship("Article", back_populates="source")

    def __repr__(self) -> str:
        return f"<Source {self.id}: {self.name} ({self.last_status})>"


class Article(Base):
    __tablename__ = "articles"

    id = Column(String(64), primary_key=True)  # SHA-256 or URL hash for deterministic uniqueness
    headline = Column(String(512), nullable=False, index=True)
    original_url = Column(String(1024), nullable=False, unique=True, index=True)
    canonical_url = Column(String(1024), nullable=True, index=True)
    publisher = Column(String(128), nullable=False, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    collected_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    language = Column(String(10), default="en", nullable=False)

    # Raw extracted content & short summary
    short_description = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    cluster_id = Column(String(64), nullable=True, index=True)  # For story deduplication & grouping

    # Editorial & Intelligence fields (English & Kannada)
    summary_en = Column(Text, nullable=True)
    summary_kn = Column(Text, nullable=True)
    detailed_summary_en = Column(Text, nullable=True)
    detailed_summary_kn = Column(Text, nullable=True)
    why_it_matters_en = Column(Text, nullable=True)
    why_it_matters_kn = Column(Text, nullable=True)
    background_en = Column(Text, nullable=True)
    background_kn = Column(Text, nullable=True)

    # JSON stored as Text for cross-SQLite portability
    important_facts = Column(Text, nullable=True)  # JSON array of strings / key stats
    tags = Column(Text, nullable=True)            # JSON array of string tags
    thumbnail_url = Column(String(1024), nullable=True)

    # User Interaction
    is_bookmarked = Column(Boolean, default=False, nullable=False, index=True)
    bookmarked_at = Column(DateTime, nullable=True)
    read_count = Column(Integer, default=0, nullable=False)
    last_read_at = Column(DateTime, nullable=True)

    # Relationships
    source_id = Column(String(64), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    source = relationship("Source", back_populates="articles")
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
    topics = relationship("EducationalTopic", secondary=article_topics, back_populates="articles")
    briefing_items = relationship("BriefingItem", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Article {self.id}: {self.headline[:40]}...>"


class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(String(64), primary_key=True)  # e.g., "briefing-2026-11-21-morning"
    briefing_type = Column(String(16), nullable=False)  # "morning" or "evening"
    briefing_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    summary_en = Column(Text, nullable=True)
    summary_kn = Column(Text, nullable=True)
    article_count = Column(Integer, default=0, nullable=False)

    # Relationships
    items = relationship("BriefingItem", back_populates="briefing", cascade="all, delete-orphan", order_by="BriefingItem.order_index")

    def __repr__(self) -> str:
        return f"<Briefing {self.id}: {self.briefing_type} ({self.article_count} articles)>"


class BriefingItem(Base):
    __tablename__ = "briefing_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    briefing_id = Column(String(64), ForeignKey("briefings.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(String(64), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(32), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    briefing = relationship("Briefing", back_populates="items")
    article = relationship("Article", back_populates="briefing_items")
    category = relationship("Category")


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    trigger_type = Column(String(32), default="scheduled", nullable=False)  # scheduled, manual, restart_recovery
    status = Column(String(32), default="running", nullable=False)          # running, completed, failed, partial

    sources_attempted = Column(Integer, default=0, nullable=False)
    sources_succeeded = Column(Integer, default=0, nullable=False)
    sources_failed = Column(Integer, default=0, nullable=False)
    articles_fetched = Column(Integer, default=0, nullable=False)
    articles_added = Column(Integer, default=0, nullable=False)
    articles_deduplicated = Column(Integer, default=0, nullable=False)
    error_log = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<CollectionRun {self.id}: {self.status} (+{self.articles_added} articles)>"


class EducationalTopic(Base):
    __tablename__ = "educational_topics"

    id = Column(String(64), primary_key=True)  # e.g., "how-rbi-monetary-policy-works"
    title_en = Column(String(256), nullable=False)
    title_kn = Column(String(256), nullable=False)
    category_id = Column(String(32), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    simple_definition_en = Column(Text, nullable=False)
    simple_definition_kn = Column(Text, nullable=False)
    background_en = Column(Text, nullable=False)
    background_kn = Column(Text, nullable=False)
    how_it_works_en = Column(Text, nullable=False)
    how_it_works_kn = Column(Text, nullable=False)
    real_world_example_en = Column(Text, nullable=False)
    real_world_example_kn = Column(Text, nullable=False)
    current_events_connection_en = Column(Text, nullable=True)
    current_events_connection_kn = Column(Text, nullable=True)

    # JSON stored as Text
    important_terminology = Column(Text, nullable=True)  # List of {term_en, term_kn, definition_en, definition_kn}
    knowledge_check = Column(Text, nullable=True)        # List of questions, options, answers, explanations

    is_featured = Column(Boolean, default=False, nullable=False)
    featured_date = Column(Date, nullable=True, index=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="educational_topics")
    articles = relationship("Article", secondary=article_topics, back_populates="topics")

    def __repr__(self) -> str:
        return f"<EducationalTopic {self.id}: {self.title_en}>"
