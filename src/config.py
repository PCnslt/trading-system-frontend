import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from enum import Enum


class ServiceType(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"


class RequestType(str, Enum):
    EMBEDDING = "embedding"
    COMPLETION = "completion"
    CHAT = "chat"


class Config(BaseSettings):
    """Main configuration for the memory system."""
    
    # Database
    database_url: str = Field(default="postgresql://memory_user:memory_password@localhost:5432/memory_system", env="DATABASE_URL")
    database_pool_size: int = Field(default=20)
    
    # Ollama
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    ollama_timeout: int = Field(default=30)
    embedding_model: str = Field(default="nomic-embed-text", env="EMBEDDING_MODEL")
    generation_model: str = Field(default="llama3.2:3b", env="GENERATION_MODEL")
    embedding_dimension: int = Field(default=768)
    
    # Search
    similarity_threshold: float = Field(default=0.7)
    max_context_tokens: int = Field(default=4096)
    
    # Cost tracking
    cost_tracking_enabled: bool = Field(default=True)
    daily_limit: float = Field(default=1.0, env="DAILY_BUDGET_LIMIT")
    weekly_limit: float = Field(default=5.0, env="WEEKLY_BUDGET_LIMIT")
    enforce_limits: bool = Field(default=False, env="BUDGET_ENFORCEMENT_ENABLED")
    
    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    model_config = ConfigDict(env_file=".env", extra="ignore")


_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get configuration singleton."""
    global _config_instance
    if _config_instance is None:
        # Load YAML config if exists
        config_path = Path("config/config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f)
            # Flatten YAML structure for Pydantic (simplistic)
            # For production, you'd want a more sophisticated merge
            flat_config = {}
            # We'll rely on environment variables and defaults
            pass
        _config_instance = Config()
    return _config_instance