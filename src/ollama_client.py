import httpx
import logging
from typing import List, Optional, Dict, Any
import hashlib
import json

from src.config import get_config
from src.models import ServiceType, RequestType

logger = logging.getLogger(__name__)
config = get_config()


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self):
        self.base_url = config.ollama_url
        self.timeout = config.ollama_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self.embedding_model = config.embedding_model
        self.generation_model = config.generation_model
        
        # Model info cache
        self._model_info: Dict[str, Any] = {}
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def ensure_model(self, model_name: str):
        """Ensure model is available, pull if not."""
        try:
            # Check if model exists
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                
                if model_name not in model_names:
                    logger.info(f"Pulling model {model_name}...")
                    pull_response = await self.client.post(
                        f"{self.base_url}/api/pull",
                        json={"name": model_name}
                    )
                    if pull_response.status_code != 200:
                        logger.error(f"Failed to pull model {model_name}")
                        raise Exception(f"Model {model_name} not available")
                    
                    logger.info(f"Model {model_name} pulled successfully")
        except Exception as e:
            logger.error(f"Failed to ensure model {model_name}: {e}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using local Ollama model."""
        try:
            # Ensure model is available
            await self.ensure_model(self.embedding_model)
            
            # Get embedding
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding")
                if embedding and len(embedding) == config.embedding_dimension:
                    return embedding
                else:
                    raise Exception(f"Invalid embedding dimension: {len(embedding)}")
            else:
                raise Exception(f"Embedding failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            raise
    
    async def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 1024) -> str:
        """Generate text using local Ollama model."""
        try:
            # Ensure model is available
            await self.ensure_model(self.generation_model)
            
            # Prepare messages
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            # Generate
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.generation_model,
                    "messages": messages,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.1  # Lower temp for factual responses
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                raise Exception(f"Generation failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to generate: {e}")
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    def get_text_hash(self, text: str) -> str:
        """Get hash of text for caching."""
        return hashlib.md5(text.encode()).hexdigest()


# Global Ollama client instance
_ollama_client: Optional[OllamaClient] = None


async def get_ollama_client() -> OllamaClient:
    """Get Ollama client singleton."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
        # Quick health check
        if not await _ollama_client.health_check():
            logger.warning("Ollama service not healthy on startup")
    return _ollama_client


async def close_ollama_client():
    """Close Ollama client."""
    global _ollama_client
    if _ollama_client is not None:
        await _ollama_client.close()
        _ollama_client = None