$body = @{
    model = "llama3.2:3b"
    prompt = "Research AI agent memory systems. Provide a comprehensive overview of current (2026) approaches, including vector databases, episodic vs semantic memory, memory-augmented neural networks, RAG for agents, memory management techniques, market trends, technical challenges, and impact on AI agent capabilities. Focus on recent advances (2025-2026). Be concise but thorough. Format with clear sections."
    stream = $false
    options = @{
        temperature = 0.7
        top_p = 0.9
    }
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
$response.response