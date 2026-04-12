#!/usr/bin/env python3
"""
Test script for Local Memory System.
Run with: python test_memory_system.py
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from memory_manager import get_memory_manager
from rag_engine import get_rag_engine
from config import get_config


async def test_memory_manager():
    """Test basic memory operations."""
    print("🧠 Testing Memory Manager...")
    
    memory_manager = await get_memory_manager()
    
    # Test storing memories
    memories = [
        {
            "content": "The capital of France is Paris.",
            "metadata": {"category": "geography", "importance": "high"},
            "tags": ["geography", "europe", "capitals"]
        },
        {
            "content": "Python is a popular programming language for AI and data science.",
            "metadata": {"category": "programming", "difficulty": "medium"},
            "tags": ["programming", "ai", "python"]
        },
        {
            "content": "Water boils at 100 degrees Celsius at sea level.",
            "metadata": {"category": "science", "verified": True},
            "tags": ["science", "physics", "chemistry"]
        }
    ]
    
    memory_ids = []
    for memory in memories:
        memory_id = await memory_manager.store(
            content=memory["content"],
            metadata=memory["metadata"],
            tags=memory["tags"]
        )
        memory_ids.append(memory_id)
        print(f"  ✅ Stored memory: {memory['content'][:50]}... (ID: {memory_id})")
    
    # Test retrieval
    print("\n🔍 Testing retrieval...")
    query = "What is the capital of France?"
    results = await memory_manager.retrieve(query=query, top_k=2)
    
    print(f"  Query: '{query}'")
    print(f"  Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"    {i+1}. {result.content[:60]}... (similarity: {result.similarity:.3f})")
    
    # Test stats
    print("\n📊 Testing statistics...")
    stats = await memory_manager.get_stats()
    print(f"  Total memories: {stats.get('total_memories', 0)}")
    print(f"  Total words: {stats.get('total_words', 0)}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    for memory_id in memory_ids:
        await memory_manager.delete(memory_id)
        print(f"  ✅ Deleted memory: {memory_id}")
    
    return True


async def test_rag_engine():
    """Test RAG functionality."""
    print("\n🤖 Testing RAG Engine...")
    
    # First store some memories
    memory_manager = await get_memory_manager()
    
    test_memories = [
        "OpenAI released GPT-4 in March 2023.",
        "Machine learning requires large datasets and computational power.",
        "Neural networks are inspired by biological brains.",
        "Transformer architecture revolutionized natural language processing."
    ]
    
    for content in test_memories:
        await memory_manager.store(
            content=content,
            metadata={"source": "test"},
            tags=["ai", "ml", "test"]
        )
    
    # Test RAG
    rag_engine = await get_rag_engine()
    
    questions = [
        "What is GPT-4?",
        "What do machine learning models need?",
        "How are neural networks inspired?"
    ]
    
    for question in questions:
        print(f"\n  Question: '{question}'")
        
        response = await rag_engine.answer(
            question=question,
            top_k=2,
            max_tokens=100
        )
        
        print(f"  Answer: {response.answer[:80]}...")
        print(f"  Sources: {len(response.sources)} memories")
        print(f"  Tokens used: {response.tokens_used}")
        print(f"  Cost: ${response.cost:.6f}")
    
    # Cleanup
    print("\n🧹 Cleaning up RAG test memories...")
    # In a real system, we'd track and delete these
    
    return True


async def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing Configuration...")
    
    config = get_config()
    
    print(f"  Database URL: {config.database_url[:30]}...")
    print(f"  Ollama URL: {config.ollama_url}")
    print(f"  Embedding model: {config.embedding_model}")
    print(f"  Generation model: {config.generation_model}")
    print(f"  Embedding dimension: {config.embedding_dimension}")
    
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting Local Memory System Tests")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 3
    
    try:
        # Test configuration
        if await test_configuration():
            tests_passed += 1
        
        # Test memory manager  
        if await test_memory_manager():
            tests_passed += 1
        
        # Test RAG engine
        if await test_rag_engine():
            tests_passed += 1
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed")
        return False


if __name__ == "__main__":
    # Set test environment variables
    os.environ["DATABASE_URL"] = "postgresql://memory_user:memory_password@localhost:5432/memory_system"
    os.environ["OLLAMA_URL"] = "http://localhost:11434"
    os.environ["EMBEDDING_MODEL"] = "nomic-embed-text"
    os.environ["GENERATION_MODEL"] = "llama3.2:3b"
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)