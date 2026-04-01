import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Text, JSON, DateTime, Float, Integer, Numeric, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Memory(Base):
    """Memory storage with vector embeddings."""
    __tablename__ = "memories"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column("embedding", Text)  # Will be handled by pgvector extension
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="'{}'::jsonb")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    embedding_model: Mapped[str] = mapped_column(String(256), nullable=False, server_default="nomic-embed-text")
    
    # Full-text search vector for hybrid search (BM25 + vector)
    search_vector = Column("search_vector", TSVECTOR)
    
    # Tags for easy filtering (extracted from metadata)
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list, server_default="'[]'::jsonb")
    
    # Importance score (0-1, can be set by user or learned)
    importance: Mapped[float] = mapped_column(Float, default=1.0, server_default="1.0")
    
    # Source information
    source: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    
    __table_args__ = (
        # GIN index for full-text search
        Index("ix_memories_search_vector", "search_vector", postgresql_using="gin"),
        # Index for tags array
        Index("ix_memories_tags", "tags", postgresql_using="gin"),
        # Index for metadata jsonb
        Index("ix_memories_metadata", "metadata", postgresql_using="gin"),
        # Composite index for common queries
        Index("ix_memories_created_source", "created_at", "source"),
    )


class APIUsage(Base):
    """API usage tracking for cost optimization."""
    __tablename__ = "api_usage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0, server_default="0.0")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    request_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="'{}'::jsonb")
    
    __table_args__ = (
        Index("ix_api_usage_service_timestamp", "service", "timestamp"),
        Index("ix_api_usage_model_timestamp", "model", "timestamp"),
        Index("ix_api_usage_request_type_timestamp", "request_type", "timestamp"),
    )


class EmbeddingCache(Base):
    """Cache for embeddings to avoid recomputation."""
    __tablename__ = "embedding_cache"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column("embedding", Text)  # Will be handled by pgvector extension
    model: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    
    __table_args__ = (
        Index("ix_embedding_cache_model_hash", "model", "text_hash"),
        Index("ix_embedding_cache_last_accessed", "last_accessed"),
    )


class MemoryConsolidationLog(Base):
    """Log of memory consolidation operations."""
    __tablename__ = "memory_consolidation_log"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    memories_affected: Mapped[List[uuid.UUID]] = mapped_column(JSONB, default=list, server_default="'[]'::jsonb")
    memories_created: Mapped[List[uuid.UUID]] = mapped_column(JSONB, default=list, server_default="'[]'::jsonb")
    memories_deleted: Mapped[List[uuid.UUID]] = mapped_column(JSONB, default=list, server_default="'[]'::jsonb")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0, server_default="0.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="'{}'::jsonb")


class SearchQueryLog(Base):
    """Log of search queries for analytics and improvement."""
    __tablename__ = "search_query_log"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # vector, text, hybrid
    filters: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="'{}'::jsonb")
    top_k: Mapped[int] = mapped_column(Integer, default=5)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    response_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    cache_hit: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, index=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="'{}'::jsonb")