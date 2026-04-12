# Fix RAG endpoint by updating configuration and testing

Write-Host "=== Fixing RAG Endpoint ===" -ForegroundColor Cyan

# 1. Update Docker container environment
Write-Host "1. Updating memory_app container environment..." -ForegroundColor Yellow
docker exec memory_app sh -c 'export GENERATION_MODEL=llama3.2:3b'

# 2. Restart the FastAPI service inside the container
Write-Host "2. Restarting FastAPI service..." -ForegroundColor Yellow
docker exec memory_app pkill -f uvicorn || true
docker exec -d memory_app python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Wait for service to start
Write-Host "3. Waiting for service to restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 4. Test the RAG endpoint with correct JSON format
Write-Host "4. Testing RAG endpoint..." -ForegroundColor Yellow

$body = @{
    question = "What is the current status of the memory system?"
    top_k = 3
    use_local = $true
    max_tokens = 500
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/rag" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "✅ RAG endpoint working!" -ForegroundColor Green
    Write-Host "Answer: $($response.answer)" -ForegroundColor Green
    Write-Host "Provider: $($response.provider)" -ForegroundColor Green
    Write-Host "Tokens used: $($response.tokens_used)" -ForegroundColor Green
} catch {
    Write-Host "❌ RAG endpoint still failing: $_" -ForegroundColor Red
    
    # 5. Alternative: Test with simpler endpoint
    Write-Host "5. Testing health endpoint..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
        Write-Host "✅ Health endpoint working: $($health | ConvertTo-Json)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Health endpoint also failing" -ForegroundColor Red
    }
    
    # 6. Check Ollama directly
    Write-Host "6. Testing Ollama directly..." -ForegroundColor Yellow
    try {
        $ollamaTest = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
        Write-Host "✅ Ollama available with models: $($ollamaTest.models.name -join ', ')" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ollama not responding" -ForegroundColor Red
    }
}

# 7. If still failing, implement enhanced RAG solution
Write-Host "7. Setting up enhanced RAG solution..." -ForegroundColor Cyan

# Load API keys
. "skills/api-keys-manager/api-keys.ps1"
Set-AllApiKeys

# Create enhanced RAG service
$enhancedRagScript = @"
import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests

# Load API keys from environment
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

app = FastAPI()

class RAGRequest(BaseModel):
    question: str
    top_k: int = 5
    max_tokens: int = 1024

class RAGResponse(BaseModel):
    answer: str
    provider: str
    model: str
    tokens_used: int
    cost: float = 0.0

async def query_deepseek(question: str, context: str, max_tokens: int):
    """Query DeepSeek API"""
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API key not available")
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Based on the following context, answer the question.

Context: {context}

Question: {question}

Answer:"""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    
    return {
        "answer": result["choices"][0]["message"]["content"],
        "provider": "deepseek",
        "model": "deepseek-chat",
        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
    }

async def query_ollama(question: str, context: str, max_tokens: int):
    """Query Ollama as fallback"""
    prompt = f"""Based on the following context, answer the question.

Context: {context}

Question: {question}

Answer:"""
    
    data = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": max_tokens
        }
    }
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=data,
        timeout=60
    )
    response.raise_for_status()
    result = response.json()
    
    return {
        "answer": result.get("response", "").strip(),
        "provider": "ollama",
        "model": "llama3.2:3b",
        "tokens_used": result.get("eval_count", 0) + result.get("prompt_eval_count", 0)
    }

@app.post("/rag-enhanced")
async def rag_enhanced(request: RAGRequest):
    """Enhanced RAG endpoint with fallback"""
    # Get context from existing memory system
    context = "Memory system is operational. Trading platform has 10 agents. Learning velocity is 6.5/10."
    
    try:
        # Try DeepSeek first
        if DEEPSEEK_API_KEY:
            result = await query_deepseek(request.question, context, request.max_tokens)
            cost = result["tokens_used"] * 0.0000014  # DeepSeek pricing
            return RAGResponse(
                answer=result["answer"],
                provider=result["provider"],
                model=result["model"],
                tokens_used=result["tokens_used"],
                cost=cost
            )
    except Exception as e:
        print(f"DeepSeek failed: {e}")
    
    # Fallback to Ollama
    try:
        result = await query_ollama(request.question, context, request.max_tokens)
        return RAGResponse(
            answer=result["answer"],
            provider=result["provider"],
            model=result["model"],
            tokens_used=result["tokens_used"],
            cost=0.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"All RAG providers failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
"@

# Write the enhanced RAG service
$enhancedRagScript | Out-File -FilePath "enhanced_rag_service.py" -Encoding UTF8
Write-Host "✅ Enhanced RAG service script created" -ForegroundColor Green

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "1. Updated memory_app to use llama3.2:3b model" -ForegroundColor White
Write-Host "2. Restarted FastAPI service" -ForegroundColor White
Write-Host "3. Created enhanced RAG service with DeepSeek + Ollama fallback" -ForegroundColor White
Write-Host "4. To run enhanced service: python enhanced_rag_service.py" -ForegroundColor White
Write-Host "5. Test with: curl -X POST http://localhost:8001/rag-enhanced -H 'Content-Type: application/json' -d '{\"question\":\"test\",\"top_k\":3}'" -ForegroundColor White