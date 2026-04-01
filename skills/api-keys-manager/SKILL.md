# API Keys Manager Skill

## Description
Centralized management of all API keys for OpenClaw and external projects. Provides secure storage, environment variable loading, and integration with OpenClaw's secrets system.

## Features
- **Secure Storage**: All API keys stored in encrypted JSON file (`~/.openclaw/secrets/api-keys.json`)
- **Environment Variables**: Auto-load keys as environment variables for any project
- **OpenClaw Integration**: Works with OpenClaw's SecretRef system
- **Cross-Project**: Keys available to all agents, skills, and external scripts
- **Security**: Masked display, secure loading, user/env persistence options

## Quick Start

### 1. Load API keys for current session:
```powershell
# Import the module
. "skills\api-keys-manager\api-keys.ps1"

# Or use the functions
Set-AllApiKeys
```

### 2. Test that keys are loaded:
```powershell
Test-ApiKeys
```

### 3. Save keys permanently (user environment):
```powershell
Save-ApiKeysToUserEnv
```

### 4. View summary (masked for security):
```powershell
Get-ApiKeySummary
```

## API Keys Included

| Category | Keys | Purpose |
|----------|------|---------|
| **AWS** | Access Key ID, Secret Access Key | Cloud services, EC2, S3 |
| **GitHub** | Token, OpenClaw Token | Repository access, automation |
| **OpenAI** | API Key, Flowise Key | AI models, GPT, embeddings |
| **HuggingFace** | Token | Free inference models |
| **Financial** | Alpha Vantage, FMP, NewsAPI, CoinMarketCap | Stock data, crypto, news |
| **DeepSeek** | API Key | Reasoning models |
| **Google** | Project ID, Search API, CSE, Gemini, OAuth | Search, AI, authentication |
| **Social** | Facebook, X/Twitter | Social media APIs |
| **Payment** | Stripe | Payment processing |
| **Communication** | Twilio, Gmail | SMS, email |
| **Vector DB** | Pinecone | Vector storage |
| **AI Providers** | OpenRouter, Groq | Alternative AI models |
| **Exchange** | Binance US, Testnet | Crypto trading |

## Integration with OpenClaw

### SecretRef Configuration
The skill integrates with OpenClaw's SecretRef system. Keys can be referenced in config:

```json
{
  "models": {
    "providers": {
      "deepseek": {
        "apiKey": {
          "source": "file",
          "provider": "filemain",
          "id": "/deepseek/apiKey"
        }
      }
    }
  }
}
```

### Automatic Loading
Add to your agent startup scripts:
```powershell
# In agent initialization
. "skills\api-keys-manager\api-keys.ps1"
```

## Security Best Practices

1. **File Permissions**: Secrets file should have restricted permissions (Windows: ACL, Linux: 600)
2. **Encryption**: Consider encrypting the JSON file for additional security
3. **Git Ignore**: Ensure `secrets/` directory is in `.gitignore`
4. **Environment Variables**: Prefer session-specific over permanent storage
5. **Rotation**: Regularly rotate sensitive keys (AWS, Stripe, etc.)

## File Structure

```
~/.openclaw/secrets/
├── api-keys.json          # Main secrets file (encrypted recommended)
└── backup/               # Key backups (optional)

skills/api-keys-manager/
├── SKILL.md             # This documentation
├── api-keys.ps1        # PowerShell module
└── load-keys.cmd       # Batch file for quick loading
```

## Troubleshooting

### "Secrets file not found"
Create the file: `New-Item -Path "~/.openclaw/secrets/api-keys.json" -Force`

### "ACL verification unavailable on Windows"
Windows ACL check may fail. For development, you can:
1. Use environment variables instead of file provider
2. Disable ACL checks in OpenClaw config (if available)

### Environment variables not persisting
- User env vars require session restart or `refreshenv`
- System env vars require administrator privileges

## Usage Examples

### For Trading Agents
```powershell
# Load financial API keys
$env:ALPHAVANTAGE_API_KEY = (Get-Content ~/.openclaw/secrets/api-keys.json | ConvertFrom-Json).alphavantage.apiKey
```

### For AI Projects
```powershell
# Load AI provider keys
. "skills\api-keys-manager\api-keys.ps1"
# Now OPENAI_API_KEY, DEEPSEEK_API_KEY, etc. are available
```

### For Web Automation
```powershell
# Load social media and search keys
$keys = Get-Content ~/.openclaw/secrets/api-keys.json | ConvertFrom-Json
$env:GOOGLE_SEARCH_API_KEY = $keys.google.searchApiKey
$env:SERPER_API_KEY = $keys.serper.apiKey
```

## Maintenance

### Adding New Keys
1. Edit `~/.openclaw/secrets/api-keys.json`
2. Add new section with key-value pairs
3. Update `api-keys.ps1` to load as environment variable
4. Test with `Set-AllApiKeys`

### Rotating Keys
1. Generate new key in service provider
2. Update value in secrets file
3. Reload environment: `Set-AllApiKeys`
4. Test functionality
5. Keep old key for rollback if needed

### Backup Strategy
```powershell
# Backup secrets file
Copy-Item ~/.openclaw/secrets/api-keys.json ~/.openclaw/secrets/backup/api-keys-$(Get-Date -Format yyyyMMdd).json
```

## License
OpenClaw Skill - Use responsibly. Keep secrets secure.