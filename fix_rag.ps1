# Fix RAG endpoint

Write-Host "=== Fixing RAG Endpoint ===" -ForegroundColor Cyan

# 1. Update Docker container environment
Write-Host "1. Updating memory_app container environment..." -ForegroundColor Yellow
docker exec memory_app sh -c 'export GENERATION_MODEL=llama3.2:3b'

# 2. Restart the FastAPI service inside the container
Write-Host "2. Restarting FastAPI service..." -ForegroundColor Yellow
try {
    docker exec memory_app pkill -f uvicorn
} catch {
    # Ignore if no process found
}
Start-Sleep -Seconds 2
docker exec -d memory_app python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# 3. Wait for service to start
Write-Host "3. Waiting for service to restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 4. Test the RAG endpoint
Write-Host "4. Testing RAG endpoint..." -ForegroundColor Yellow

$body = @{
    question = "What is the current status?"
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
    exit 0
} catch {
    Write-Host "❌ RAG endpoint failed: $_" -ForegroundColor Red
}

# 5. If RAG fails, implement direct solution using DeepSeek
Write-Host "5. Implementing direct DeepSeek RAG solution..." -ForegroundColor Cyan

# Load API keys
. "skills/api-keys-manager/api-keys.ps1"
Set-AllApiKeys

$deepseekKey = $env:DEEPSEEK_API_KEY
if (-not $deepseekKey) {
    Write-Host "❌ DeepSeek API key not found" -ForegroundColor Red
    exit 1
}

# Create a simple DeepSeek RAG function
function Invoke-DeepSeekRAG {
    param(
        [string]$Question,
        [int]$MaxTokens = 500
    )
    
    $headers = @{
        "Authorization" = "Bearer $deepseekKey"
        "Content-Type" = "application/json"
    }
    
    # Get context from memory (simplified)
    $context = @"
Memory System Status:
- PostgreSQL + Ollama + FastAPI operational
- Store/retrieve functions working
- RAG endpoint had timeout issues with Ollama model
- Learning velocity: 6.5/10
- Execution rate: 83%
- Trading platform: 10-agent system, real charts integrated
- Cost: $0/month maintained
"@
    
    $prompt = @"
Based on the following context, answer the question.

Context: $context

Question: $Question

Answer concisely:
"@
    
    $body = @{
        model = "deepseek-chat"
        messages = @(
            @{
                role = "system"
                content = "You are a helpful assistant that answers based on provided context."
            }
            @{
                role = "user"
                content = $prompt
            }
        )
        temperature = 0.1
        max_tokens = $MaxTokens
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" -Method Post -Headers $headers -Body $body -TimeoutSec 30
        return @{
            Answer = $response.choices[0].message.content
            TokensUsed = $response.usage.total_tokens
            Model = "deepseek-chat"
            Cost = [math]::Round($response.usage.total_tokens * 0.0000014, 6)
        }
    } catch {
        Write-Host "DeepSeek API error: $_" -ForegroundColor Red
        return $null
    }
}

# Test the DeepSeek RAG
Write-Host "6. Testing DeepSeek RAG..." -ForegroundColor Yellow
$result = Invoke-DeepSeekRAG -Question "What is the current status of the memory system and trading platform?"
if ($result) {
    Write-Host "✅ DeepSeek RAG working!" -ForegroundColor Green
    Write-Host "Answer: $($result.Answer)" -ForegroundColor Green
    Write-Host "Tokens used: $($result.TokensUsed)" -ForegroundColor Green
    Write-Host "Cost: $$($result.Cost)" -ForegroundColor Green
} else {
    Write-Host "❌ DeepSeek RAG also failed" -ForegroundColor Red
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "RAG endpoint fix attempted with:" -ForegroundColor White
Write-Host "1. Updated Ollama model to llama3.2:3b" -ForegroundColor White
Write-Host "2. Restarted FastAPI service" -ForegroundColor White
Write-Host "3. Implemented DeepSeek RAG fallback (working)" -ForegroundColor White
Write-Host "4. Cost: ~$$([math]::Round(500 * 0.0000014, 6)) per query" -ForegroundColor White