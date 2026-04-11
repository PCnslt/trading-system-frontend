import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from src.database import Database
from src.ollama_client import get_ollama_client, OllamaClient
from src.cost_tracker import get_cost_tracker
from src.models import MemoryCreate, MemoryResponse, ServiceType, RequestType
from src.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class MemoryManager:
    """Manage memories with vector embeddings."""
    
    def __init__(self):
        self.ollama_client: Optional[OllamaClient] = None
        self.cost_tracker = get_cost_tracker()
        self.embedding_dimension = config.embedding_dimension
        
    async def _get_ollama_client(self) -> OllamaClient:
        """Lazy load Ollama client."""
        if self.ollama_client is None:
            self.ollama_client = await get_ollama_client()
        return self.ollama_client
    
    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Store a memory with embedding."""
        try:
            # Get embedding
            ollama = await self._get_ollama_client()
            embedding = await ollama.get_embedding(content)
            # Convert to string representation for PostgreSQL vector type
            embedding_str = '[' + ','.join(str(v) for v in embedding) + ']'
            
            # Log cost (local = $0)
            await self.cost_tracker.log_usage(
                service=ServiceType.LOCAL,
                model=config.embedding_model,
                input_tokens=len(content.split()),
                output_tokens=0,
                request_type=RequestType.EMBEDDING
            )
            
            # Prepare metadata
            full_metadata = metadata or {}
            if tags:
                full_metadata["tags"] = tags
            full_metadata["content_length"] = len(content)
            full_metadata["word_count"] = len(content.split())
            
            # Store in database
            memory_id = str(uuid.uuid4())
            pool = await Database.get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO memories 
                    (id, content, embedding, metadata, embedding_model)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                memory_id, content, embedding_str, json.dumps(full_metadata),
                config.embedding_model)
            
            logger.info(f"Memory stored with ID: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> List[MemoryResponse]:
        """Retrieve similar memories."""
        try:
            # Get query embedding
            ollama = await self._get_ollama_client()
            query_embedding = await ollama.get_embedding(query)
            # Convert to string representation for PostgreSQL vector type
            query_embedding_str = '[' + ','.join(str(v) for v in query_embedding) + ']'
            
            # Log cost (local = $0)
            await self.cost_tracker.log_usage(
                service=ServiceType.LOCAL,
                model=config.embedding_model,
                input_tokens=len(query.split()),
                output_tokens=0,
                request_type=RequestType.EMBEDDING
            )
            
            # Build filter conditions
            filter_conditions = []
            filter_params = [query_embedding_str, top_k]
            
            if filters:
                for i, (key, value) in enumerate(filters.items(), start=3):
                    filter_conditions.append(f"metadata->>'{key}' = ${i}")
                    filter_params.append(value)
            
            filter_clause = ""
            if filter_conditions:
                filter_clause = f"AND {' AND '.join(filter_conditions)}"
            
            # Search in database
            pool = await Database.get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(f"""
                    SELECT 
                        id,
                        content,
                        metadata,
                        created_at,
                        last_accessed,
                        1 - (embedding <=> $1) as similarity
                    FROM memories
                    WHERE 1 - (embedding <=> $1) > $3
                    {filter_clause}
                    ORDER BY embedding <=> $1
                    LIMIT $2
                """, *filter_params, config.similarity_threshold)
            
            # Convert to response objects
            memories = []
            for row in rows:
                memory = MemoryResponse(
                    id=str(row["id"]),
                    content=row["content"],
                    metadata=json.loads(row["metadata"]),
                    similarity=float(row["similarity"]),
                    created_at=row["created_at"],
                    last_accessed=row["last_accessed"]
                )
                memories.append(memory)
            
            logger.debug(f"Retrieved {len(memories)} memories for query: {query[:50]}...")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            raise
    
    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a memory, re-embedding if content changed."""
        try:
            pool = await Database.get_pool()
            
            if content is not None:
                # Get new embedding
                ollama = await self._get_ollama_client()
                embedding = await ollama.get_embedding(content)
                # Convert to string representation for PostgreSQL vector type
                embedding_str = '[' + ','.join(str(v) for v in embedding) + ']'
                
                # Log cost
                await self.cost_tracker.log_usage(
                    service=ServiceType.LOCAL,
                    model=config.embedding_model,
                    input_tokens=len(content.split()),
                    output_tokens=0,
                    request_type=RequestType.EMBEDDING
                )
                
                # Update with new embedding
                if metadata is not None:
                    await pool.execute("""
                        UPDATE memories 
                        SET content = $1, 
                            embedding = $2, 
                            metadata = $3,
                            embedding_model = $4
                        WHERE id = $5
                    """, content, embedding_str, json.dumps(metadata),
                    config.embedding_model, uuid.UUID(memory_id))
                else:
                    await pool.execute("""
                        UPDATE memories 
                        SET content = $1, 
                            embedding = $2,
                            embedding_model = $3
                        WHERE id = $4
                    """, content, embedding_str, config.embedding_model,
                    uuid.UUID(memory_id))
            elif metadata is not None:
                # Just update metadata
                await pool.execute("""
                    UPDATE memories 
                    SET metadata = $1
                    WHERE id = $2
                """, json.dumps(metadata), uuid.UUID(memory_id))
            else:
                # Nothing to update
                return False
            
            logger.info(f"Memory updated: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
    
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        try:
            pool = await Database.get_pool()
            result = await pool.execute(
                "DELETE FROM memories WHERE id = $1",
                uuid.UUID(memory_id)
            )
            
            deleted = result.split()[1]  # e.g., "DELETE 1"
            success = deleted == "1"
            
            if success:
                logger.info(f"Memory deleted: {memory_id}")
            else:
                logger.warning(f"Memory not found: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise
    
    async def search_by_tags(self, tags: List[str]) -> List[MemoryResponse]:
        """Search memories by tags."""
        try:
            pool = await Database.get_pool()
            
            # Build tag filter conditions
            tag_conditions = []
            for i, tag in enumerate(tags, start=1):
                tag_conditions.append(f"metadata->'tags' @> ${i}::jsonb")
            
            query = f"""
                SELECT 
                    id,
                    content,
                    metadata,
                    created_at,
                    last_accessed
                FROM memories
                WHERE {' AND '.join(tag_conditions)}
                ORDER BY created_at DESC
                LIMIT 100
            """
            
            rows = await pool.fetch(query, *[json.dumps([tag]) for tag in tags])
            
            # Convert to response objects
            memories = []
            for row in rows:
                memory = MemoryResponse(
                    id=str(row["id"]),
                    content=row["content"],
                    metadata=json.loads(row["metadata"]),
                    created_at=row["created_at"],
                    last_accessed=row["last_accessed"]
                )
                memories.append(memory)
            
            logger.debug(f"Found {len(memories)} memories with tags: {tags}")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search by tags: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        try:
            pool = await Database.get_pool()
            
            # Get basic counts
            total_memories = await pool.fetchval("SELECT COUNT(*) FROM memories")
            total_words = await pool.fetchval("""
                SELECT SUM((metadata->>'word_count')::int) FROM memories
            """) or 0
            
            # Get age distribution
            age_distribution = await pool.fetch("""
                SELECT 
                    CASE 
                        WHEN created_at > NOW() - INTERVAL '1 day' THEN 'last_day'
                        WHEN created_at > NOW() - INTERVAL '1 week' THEN 'last_week'
                        WHEN created_at > NOW() - INTERVAL '1 month' THEN 'last_month'
                        ELSE 'older'
                    END as age_group,
                    COUNT(*) as count
                FROM memories
                GROUP BY age_group
            """)
            
            # Get tag statistics
            tag_stats = await pool.fetch("""
                SELECT 
                    jsonb_array_elements_text(metadata->'tags') as tag,
                    COUNT(*) as count
                FROM memories
                WHERE metadata ? 'tags'
                GROUP BY tag
                ORDER BY count DESC
                LIMIT 10
            """)
            
            return {
                "total_memories": total_memories,
                "total_words": total_words,
                "age_distribution": {row["age_group"]: row["count"] for row in age_distribution},
                "top_tags": {row["tag"]: row["count"] for row in tag_stats},
                "embedding_model": config.embedding_model,
                "embedding_dimension": config.embedding_dimension
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


async def get_memory_manager() -> MemoryManager:
    """Get memory manager singleton."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager