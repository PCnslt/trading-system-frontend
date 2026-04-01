from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MemoryCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)


class MemoryResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    similarity: Optional[float] = None
    created_at: datetime
    last_accessed: datetime


class SearchQuery(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None
    use_cache: bool = True


class RAGQuery(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    use_local: bool = True
    max_tokens: int = Field(default=1024, ge=1, le=4096)


class RAGResponse(BaseModel):
    answer: str
    sources: List[MemoryResponse]
    tokens_used: int
    cost: float = 0.0
    model_used: str


class APIUsage(BaseModel):
    service: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    request_type: str
    endpoint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ServiceType(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class RequestType(str, Enum):
    EMBEDDING = "embedding"
    COMPLETION = "completion"
    CHAT = "chat"