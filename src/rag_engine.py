import logging
from typing import List, Optional
import tiktoken  # For token counting

from src.memory_manager import get_memory_manager, MemoryManager
from src.ollama_client import get_ollama_client, OllamaClient
from src.cost_tracker import get_cost_tracker
from src.models import RAGQuery, RAGResponse, MemoryResponse, ServiceType, RequestType
from src.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class RAGEngine:
    """Retrieval-Augmented Generation engine."""
    
    def __init__(self):
        self.memory_manager: Optional[MemoryManager] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.cost_tracker = get_cost_tracker()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        
    async def _get_memory_manager(self) -> MemoryManager:
        """Lazy load memory manager."""
        if self.memory_manager is None:
            self.memory_manager = await get_memory_manager()
        return self.memory_manager
    
    async def _get_ollama_client(self) -> OllamaClient:
        """Lazy load Ollama client."""
        if self.ollama_client is None:
            self.ollama_client = await get_ollama_client()
        return self.ollama_client
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))
    
    def _format_context(
        self,
        memories: List[MemoryResponse],
        max_tokens: int
    ) -> str:
        """Format retrieved memories into context, respecting token limits."""
        context_parts = []
        total_tokens = 0
        
        for memory in memories:
            # Format memory for context
            memory_text = f"Memory (relevance: {memory.similarity:.2f}):\n{memory.content}\n"
            memory_tokens = self._count_tokens(memory_text)
            
            # Check if adding this would exceed limit
            if total_tokens + memory_tokens > max_tokens:
                # Try to truncate
                if total_tokens < max_tokens:
                    # Calculate how many tokens we can add
                    remaining_tokens = max_tokens - total_tokens
                    if remaining_tokens > 100:  # Minimum useful length
                        # Truncate memory
                        truncated_text = self.tokenizer.decode(
                            self.tokenizer.encode(memory_text)[:remaining_tokens]
                        )
                        context_parts.append(truncated_text + "...\n")
                        total_tokens += remaining_tokens
                break
            
            context_parts.append(memory_text)
            total_tokens += memory_tokens
        
        return "\n".join(context_parts)
    
    async def answer(
        self,
        question: str,
        top_k: int = 5,
        use_local: bool = True,
        max_tokens: int = 1024
    ) -> RAGResponse:
        """Answer a question using RAG."""
        try:
            # 1. Retrieve relevant memories
            memory_manager = await self._get_memory_manager()
            memories = await memory_manager.retrieve(
                query=question,
                top_k=top_k
            )
            
            if not memories:
                logger.warning(f"No memories found for question: {question[:50]}...")
                # Fallback to generation without context
                return await self._generate_without_context(
                    question, use_local, max_tokens
                )
            
            # 2. Format context (respect token limits)
            # Reserve tokens for question, system prompt, and answer
            context_max_tokens = config.max_context_tokens - max_tokens - 200
            context = self._format_context(memories, context_max_tokens)
            
            # 3. Prepare system prompt
            system_prompt = """You are a helpful assistant with access to a memory system.
Use the provided memories to answer the question accurately.
If the memories don't contain relevant information, say so.
Be concise and factual."""
            
            # 4. Prepare user prompt with context
            user_prompt = f"""Context from memory system:
{context}

Question: {question}

Answer based on the context above:"""
            
            # 5. Generate answer
            ollama = await self._get_ollama_client()
            answer = await ollama.generate(
                prompt=user_prompt,
                system=system_prompt,
                max_tokens=max_tokens
            )
            
            # 6. Log generation cost (local = $0)
            input_tokens = self._count_tokens(user_prompt + system_prompt)
            output_tokens = self._count_tokens(answer)
            
            await self.cost_tracker.log_usage(
                service=ServiceType.LOCAL,
                model=config.generation_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                request_type=RequestType.CHAT
            )
            
            # 7. Return response
            return RAGResponse(
                answer=answer,
                sources=memories,
                tokens_used=input_tokens + output_tokens,
                cost=0.0,  # Local = free
                model_used=config.generation_model
            )
            
        except Exception as e:
            logger.error(f"RAG failed for question '{question[:50]}...': {e}")
            raise
    
    async def _generate_without_context(
        self,
        question: str,
        use_local: bool,
        max_tokens: int
    ) -> RAGResponse:
        """Generate answer without memory context (fallback)."""
        try:
            ollama = await self._get_ollama_client()
            
            system_prompt = "You are a helpful assistant. Answer the question concisely."
            answer = await ollama.generate(
                prompt=question,
                system=system_prompt,
                max_tokens=max_tokens
            )
            
            # Log cost
            input_tokens = self._count_tokens(question + system_prompt)
            output_tokens = self._count_tokens(answer)
            
            await self.cost_tracker.log_usage(
                service=ServiceType.LOCAL,
                model=config.generation_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                request_type=RequestType.CHAT
            )
            
            return RAGResponse(
                answer=answer,
                sources=[],
                tokens_used=input_tokens + output_tokens,
                cost=0.0,
                model_used=config.generation_model
            )
            
        except Exception as e:
            logger.error(f"Generation without context failed: {e}")
            raise
    
    async def query_with_sources(
        self,
        rag_query: RAGQuery
    ) -> RAGResponse:
        """Convenience method for RAGQuery."""
        return await self.answer(
            question=rag_query.question,
            top_k=rag_query.top_k,
            use_local=rag_query.use_local,
            max_tokens=rag_query.max_tokens
        )


# Global RAG engine instance
_rag_engine: Optional[RAGEngine] = None


async def get_rag_engine() -> RAGEngine:
    """Get RAG engine singleton."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine