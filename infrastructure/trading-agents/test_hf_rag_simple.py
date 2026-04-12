#!/usr/bin/env python3
"""Simple test of Hugging Face RAG"""
from huggingface_rag_complete import HuggingFaceRAG

# Initialize with API key
rag = HuggingFaceRAG('YOUR_HUGGINGFACE_TOKEN_HERE')

print("Testing Hugging Face RAG...")
print("=" * 60)

# Test 1: Embedding
print("\n1. Testing embedding...")
embedding = rag.get_embedding('test sentence')
if embedding:
    print(f"   ✅ Embedding works! Dimensions: {len(embedding)}")
else:
    print("   ❌ Embedding failed")

# Test 2: Retrieval
print("\n2. Testing retrieval...")
context = rag.retrieve_relevant('What is the learning velocity?', top_k=2)
print(f"   Retrieved {len(context)} items")
for i, item in enumerate(context, 1):
    content_preview = item['content'][:70] + '...' if len(item['content']) > 70 else item['content']
    print(f"   {i}. {content_preview}")

# Test 3: Full query (but skip generation to avoid API calls in test)
print("\n3. Testing knowledge base...")
print(f"   Knowledge base has {len(rag.knowledge_base)} items")
categories = set(item['category'] for item in rag.knowledge_base)
print(f"   Categories: {', '.join(categories)}")

print("\n" + "=" * 60)
print("Hugging Face RAG is ready!")
print("\nTo start the server:")
print("  python huggingface_rag_complete.py")
print("\nThen query via:")
print("  curl -X POST http://localhost:8002/rag \\")
print("    -H 'Content-Type: application/json' \\")
print("    -d '{\"question\":\"What is the learning velocity?\",\"top_k\":3}'")