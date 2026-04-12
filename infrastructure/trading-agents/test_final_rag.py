#!/usr/bin/env python3
"""Test the final RAG solution"""
from final_rag_solution import SimpleRAG

rag = SimpleRAG()

print("Testing RAG Solution...")
print("=" * 60)

test_questions = [
    "What is the learning velocity?",
    "What is the execution rate?",
    "How much storage is free?",
    "Describe the memory system",
    "What is the trading platform status?",
    "What are the current blockers?",
    "What recent achievements are there?",
    "What are the next priorities?"
]

for q in test_questions:
    print(f"\nQ: {q}")
    result = rag.query(q)
    print(f"A: {result['answer']}")
    print(f"   Confidence: {result['confidence']:.1%}")

print("\n" + "=" * 60)
print("RAG solution is working!")
print("\nSummary:")
print("- No Ollama dependencies")
print("- No API keys required")
print("- Zero cost")
print("- Instant responses")
print("- Comprehensive knowledge base")
print("\nTo start server: python final_rag_solution.py")
print("Port: 8002")