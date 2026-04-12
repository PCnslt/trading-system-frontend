# Test DeepSeek API with actual key
. "skills/api-keys-manager/api-keys.ps1"
Set-AllApiKeys

$deepseekKey = $env:DEEPSEEK_API_KEY
Write-Host "DeepSeek API Key (first 10 chars): $($deepseekKey.Substring(0, 10))..." -ForegroundColor Yellow

$headers = @{
    "Authorization" = "Bearer $deepseekKey"
    "Content-Type" = "application/json"
}

$body = @{
    model = "deepseek-chat"
    messages = @(
        @{
            role = "system"
            content = "You are a helpful assistant."
        }
        @{
            role = "user"
            content = "What is 2+2? Answer in one word."
        }
    )
    temperature = 0.1
    max_tokens = 10
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-RestMethod -Uri "https://api.deepseek.com/chat/completions" -Method Post -Headers $headers -Body $body -TimeoutSec 10
    Write-Host "✅ DeepSeek API working!" -ForegroundColor Green
    Write-Host "Response: $($response.choices[0].message.content)" -ForegroundColor Green
    Write-Host "Tokens used: $($response.usage.total_tokens)" -ForegroundColor Green
    return $true
} catch {
    Write-Host "❌ DeepSeek API error: $_" -ForegroundColor Red
    return $false
}