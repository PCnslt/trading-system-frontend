import asyncio
import sys
sys.path.append('src')
from src.ollama_client import get_ollama_client

async def test():
    client = await get_ollama_client()
    try:
        print("Testing generate with qwen2.5:0.5b...")
        result = await client.generate('Hello', system='You are a helpful assistant', max_tokens=10)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())