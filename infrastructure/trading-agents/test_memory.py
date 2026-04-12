import requests
import json

print("Testing memory system integration...")

# 1. Store a memory
print("\n1. Storing memory...")
store_data = {
    "content": "Another test memory for retrieval testing",
    "tags": ["test", "retrieval", "integration"]
}
store_resp = requests.post('http://localhost:8000/memories', json=store_data)
print(f"   Status: {store_resp.status_code}")
if store_resp.status_code == 200:
    store_result = store_resp.json()
    memory_id = store_result.get('id')
    print(f"   Memory ID: {memory_id}")
else:
    print(f"   Error: {store_resp.text}")
    exit(1)

# 2. Retrieve similar memories
print("\n2. Retrieving similar memories...")
retrieve_data = {
    "query": "test memory retrieval",
    "top_k": 5
}
retrieve_resp = requests.post('http://localhost:8000/memories/retrieve', json=retrieve_data)
print(f"   Status: {retrieve_resp.status_code}")
if retrieve_resp.status_code == 200:
    memories = retrieve_resp.json()
    print(f"   Found {len(memories)} memories")
    for i, m in enumerate(memories):
        print(f"   {i+1}. {m['id'][:8]}...: {m['content'][:60]}... (similarity: {m.get('similarity', 0):.3f})")
else:
    print(f"   Error: {retrieve_resp.text}")
    exit(1)

# 3. Test RAG endpoint
print("\n3. Testing RAG endpoint...")
rag_data = {
    "question": "What test memories are stored?",
    "top_k": 3,
    "max_tokens": 200
}
rag_resp = requests.post('http://localhost:8000/rag', json=rag_data)
print(f"   Status: {rag_resp.status_code}")
if rag_resp.status_code == 200:
    rag_result = rag_resp.json()
    print(f"   Answer: {rag_result.get('answer', '')[:100]}...")
    print(f"   Sources: {len(rag_result.get('sources', []))}")
    print(f"   Tokens used: {rag_result.get('tokens_used', 0)}")
    print(f"   Cost: ${rag_result.get('cost', 0):.6f}")
else:
    print(f"   Error: {rag_resp.text}")

print("\n✅ Memory system integration test complete.")