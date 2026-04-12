$body = @{
    model = "llama3.2:3b"
    prompt = "Provide a comprehensive overview of AI agent memory systems in 2026. Include vector databases, episodic/semantic memory, RAG, memory management, market trends, challenges, and impact. Be concise."
    stream = $false
    options = @{
        temperature = 0.7
        top_p = 0.9
        num_predict = 800
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
    $response.response
} catch {
    Write-Error "Failed: $_"
}