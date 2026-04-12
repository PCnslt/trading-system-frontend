$secretsPath = "C:\Users\pcnsl\.openclaw\secrets\api-keys.json"
$secrets = Get-Content $secretsPath | ConvertFrom-Json
$token = $secrets.huggingface.token
Write-Host "Token length: $($token.Length)"

# Test HuggingFace Inference API for meta-llama/Llama-3.3-70B-Instruct
$url = "https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct"
$headers = @{
    "Authorization" = "Bearer $token"
}
try {
    $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
    Write-Host "Model accessible: $($response)"
} catch {
    Write-Host "Error: $_"
    Write-Host "Status code: $($_.Exception.Response.StatusCode.Value__)"
}