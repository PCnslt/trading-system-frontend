$response = echo "What is 2+2?" | ollama run llama3.2:3b 2>&1
Write-Host "Response: $response"