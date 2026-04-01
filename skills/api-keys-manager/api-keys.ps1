# API Keys Manager - PowerShell Module for loading all API keys as environment variables
# Created: 2026-04-01
# Usage: . .\api-keys.ps1

function Set-AllApiKeys {
    <#
    .SYNOPSIS
    Sets all API keys as environment variables for the current session.
    
    .DESCRIPTION
    Loads API keys from the centralized secrets file and sets them as environment variables.
    This makes them available to all processes in the current session.
    
    .EXAMPLE
    Set-AllApiKeys
    #>
    
    # Load the secrets JSON file
    $secretsPath = "C:\Users\pcnsl\.openclaw\secrets\api-keys.json"
    
    if (-not (Test-Path $secretsPath)) {
        Write-Error "Secrets file not found at: $secretsPath"
        return $false
    }
    
    $secrets = Get-Content $secretsPath | ConvertFrom-Json
    
    # AWS
    $env:AWS_ACCESS_KEY_ID = $secrets.aws.accessKeyId
    $env:AWS_SECRET_ACCESS_KEY = $secrets.aws.secretAccessKey
    
    # GitHub
    $env:GITHUB_TOKEN = $secrets.github.token
    $env:GITHUB_OPENCLAW_TOKEN = $secrets.github.openclawToken
    
    # OpenAI
    $env:OPENAI_API_KEY = $secrets.openai.apiKey
    $env:FLOWISE_OPENAI_API_KEY = $secrets.openai.flowiseApiKey
    
    # HuggingFace
    $env:HUGGINGFACE_TOKEN = $secrets.huggingface.token
    $env:HF_TOKEN = $secrets.huggingface.token
    
    # Financial APIs
    $env:ALPHAVANTAGE_API_KEY = $secrets.alphavantage.apiKey
    $env:FMP_API_KEY = $secrets.financialmodelingprep.apiKey
    $env:NEWSAPI_ORG_API_KEY = $secrets.newsapi.apiKey
    $env:COINMARKETCAP_API_KEY = $secrets.coinmarketcap.apiKey
    
    # DeepSeek
    $env:DEEPSEEK_API_KEY = $secrets.deepseek.apiKey
    
    # Weather
    $env:OPENWEATHERMAP_API_KEY = $secrets.openweathermap.apiKey
    
    # Facebook
    $env:FACEBOOK_UI_TOKEN = $secrets.facebook.uiToken
    $env:FACEBOOK_API_TOKEN = $secrets.facebook.apiToken
    
    # Serper
    $env:SERPER_API_KEY = $secrets.serper.apiKey
    
    # Stripe
    $env:STRIPE_SECRET_KEY = $secrets.stripe.secretKey
    $env:STRIPE_PUBLISHABLE_KEY = $secrets.stripe.publishableKey
    
    # Google
    $env:GOOGLE_PROJECT_ID = $secrets.google.projectId
    $env:GOOGLE_SEARCH_API_KEY = $secrets.google.searchApiKey
    $env:GOOGLE_CSE_ID = $secrets.google.cseId
    $env:GEMINI_PROJECT_ID = $secrets.google.geminiProjectId
    $env:GEIMINI_API_KEY = $secrets.google.geminiApiKey
    $env:GOOGLE_CLIENT_ID = $secrets.google.clientId
    $env:GOOGLE_CLIENT_SECRET = $secrets.google.clientSecret
    
    # Groq
    $env:GROQ_API_KEY = $secrets.groq.apiKey
    
    # Binance
    $env:BINANCE_US_API_KEY = $secrets.binance.usApiKey
    $env:BINANCE_US_SECRET_KEY = $secrets.binance.usSecretKey
    $env:BINANCE_TESTNET_API_KEY = $secrets.binance.testnetApiKey
    $env:BINANCE_TESTNET_SECRET_KEY = $secrets.binance.testnetSecretKey
    
    # X/Twitter
    $env:X_V2_API_KEY = $secrets.x_twitter.v2ApiKey
    $env:X_V2_API_KEY_SECRET = $secrets.x_twitter.v2ApiKeySecret
    $env:X_V2_API_BEARER_TOKEN = $secrets.x_twitter.v2BearerToken
    $env:X_V2_API_ACCESS_TOKEN = $secrets.x_twitter.v2AccessToken
    $env:X_V2_API_ACCESS_TOKEN_SECRET = $secrets.x_twitter.v2AccessTokenSecret
    
    # Gmail
    $env:GMAIL_EMAIL = $secrets.gmail.email
    $env:GMAIL_PASSWORD = $secrets.gmail.password
    
    # Twilio
    $env:TWILIO_ACCOUNT_SID = $secrets.twilio.accountSid
    $env:TWILIO_AUTH_TOKEN = $secrets.twilio.authToken
    $env:TWILIO_PHONE_NUMBER = $secrets.twilio.phoneNumber
    
    # Pinecone
    $env:PINECONE_API_KEY = $secrets.pinecone.apiKey
    
    # OpenRouter
    $env:OPENROUTER_API_KEY = $secrets.openrouter.apiKey
    
    # OpenClaw OpenAI
    $env:OPENCLAW_OPENAI_API_KEY = $secrets.openclaw.openaiApiKey
    
    Write-Host "✅ All API keys loaded as environment variables." -ForegroundColor Green
    Write-Host "Total keys loaded: $($secrets.PSObject.Properties.Count) categories" -ForegroundColor Cyan
    
    return $true
}

function Test-ApiKeys {
    <#
    .SYNOPSIS
    Tests that all API keys are properly set as environment variables.
    
    .DESCRIPTION
    Checks each environment variable and reports which ones are set/missing.
    
    .EXAMPLE
    Test-ApiKeys
    #>
    
    $keys = @(
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "GITHUB_TOKEN",
        "OPENAI_API_KEY",
        "HUGGINGFACE_TOKEN",
        "DEEPSEEK_API_KEY",
        "OPENROUTER_API_KEY"
    )
    
    $results = @()
    foreach ($key in $keys) {
        $value = [Environment]::GetEnvironmentVariable($key)
        $status = if ($value) { "✅" } else { "❌" }
        $results += [PSCustomObject]@{
            Key = $key
            Status = $status
            Value = if ($value) { "Set ($($value.Length) chars)" } else { "Not set" }
        }
    }
    
    $results | Format-Table -AutoSize
}

function Save-ApiKeysToUserEnv {
    <#
    .SYNOPSIS
    Saves API keys permanently to user environment variables.
    
    .DESCRIPTION
    Writes API keys to the Windows registry so they persist across sessions.
    Requires administrator privileges.
    
    .EXAMPLE
    Save-ApiKeysToUserEnv
    #>
    
    # Load keys first
    Set-AllApiKeys
    
    # Get all environment variables starting with our prefixes
    $envVars = Get-ChildItem Env: | Where-Object {
        $_.Name -match "^(AWS|GITHUB|OPENAI|HUGGINGFACE|DEEPSEEK|OPENROUTER|GOOGLE|GROQ|BINANCE|TWILIO|PINECONE|X_|STRIPE|SERPER|COINMARKETCAP|NEWSAPI|FMP|ALPHAVANTAGE|FACEBOOK|FLOWISE|GMAIL)_"
    }
    
    foreach ($envVar in $envVars) {
        [Environment]::SetEnvironmentVariable($envVar.Name, $envVar.Value, "User")
        Write-Host "Saved to user environment: $($envVar.Name)" -ForegroundColor Yellow
    }
    
    Write-Host "✅ API keys saved to user environment variables." -ForegroundColor Green
    Write-Host "Restart your terminal or run 'refreshenv' to load them in new sessions." -ForegroundColor Cyan
}

function Get-ApiKeySummary {
    <#
    .SYNOPSIS
    Shows a summary of all API keys (masked for security).
    
    .DESCRIPTION
    Displays a formatted table of all API keys with masked values for security.
    
    .EXAMPLE
    Get-ApiKeySummary
    #>
    
    $secretsPath = "C:\Users\pcnsl\.openclaw\secrets\api-keys.json"
    
    if (-not (Test-Path $secretsPath)) {
        Write-Error "Secrets file not found at: $secretsPath"
        return
    }
    
    $secrets = Get-Content $secretsPath | ConvertFrom-Json
    
    $summary = @()
    
    foreach ($category in $secrets.PSObject.Properties) {
        foreach ($key in $category.Value.PSObject.Properties) {
            $value = $key.Value.ToString()
            $masked = if ($value.Length -gt 8) {
                $value.Substring(0, 4) + "..." + $value.Substring($value.Length - 4)
            } else {
                "***"
            }
            
            $summary += [PSCustomObject]@{
                Category = $category.Name
                Key = $key.Name
                MaskedValue = $masked
                Length = $value.Length
            }
        }
    }
    
    $summary | Format-Table -AutoSize
}

# Export functions
Export-ModuleMember -Function Set-AllApiKeys, Test-ApiKeys, Save-ApiKeysToUserEnv, Get-ApiKeySummary

# Auto-load keys when module is imported
Set-AllApiKeys