# Memory System Integration Skill

**Integrate OpenClaw with the Local Memory System for persistent memory, RAG, and cost optimization.**

## 🎯 Purpose
Connect OpenClaw agent workflows to the production-ready local memory system (PostgreSQL + Ollama + FastAPI) for:
- Persistent storage of learnings and decisions
- Retrieval-augmented generation (RAG) for context-aware answers
- Cost tracking and optimization (100% free local models)
- Vector similarity search across all agent memories

## 🚀 Quick Start

### Prerequisites
- Local Memory System running (`docker-compose up -d` in workspace root)
- Services accessible at:
  - PostgreSQL: `localhost:5432`
  - Ollama: `localhost:11434` 
  - FastAPI: `localhost:8000`

### Basic Integration
```powershell
# Store a memory
curl -X POST http://localhost:8000/memories `
  -H "Content-Type: application/json" `
  -d '{
    "content": "Today I learned that building Windows-native PowerShell tools is better than fixing incompatible Node.js tools.",
    "metadata": {"source": "agent-learning", "date": "2026-03-31"},
    "tags": ["learning", "windows", "execution"]
  }'

# Ask a RAG question
curl -X POST http://localhost:8000/rag `
  -H "Content-Type: application/json" `
  -d '{
    "question": "What have I learned about Windows compatibility?",
    "top_k": 5,
    "max_tokens": 200
  }'
```

## 🔧 API Wrapper Functions

### PowerShell Module
Save as `skills/memory-system-integration/memory.ps1`:

```powershell
$MemoryApiUrl = "http://localhost:8000"

function Store-Memory {
    param(
        [string]$Content,
        [hashtable]$Metadata = @{},
        [string[]]$Tags = @()
    )
    
    $body = @{
        content = $Content
        metadata = $Metadata
        tags = $Tags
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$MemoryApiUrl/memories" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    return $response
}

function Query-Memory {
    param(
        [string]$Query,
        [int]$TopK = 5,
        [hashtable]$Filters = @{}
    )
    
    $body = @{
        query = $Query
        top_k = $TopK
        filters = $Filters
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$MemoryApiUrl/memories/retrieve" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    return $response
}

function Ask-WithContext {
    param(
        [string]$Question,
        [int]$TopK = 5,
        [int]$MaxTokens = 500
    )
    
    $body = @{
        question = $Question
        top_k = $TopK
        max_tokens = $MaxTokens
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$MemoryApiUrl/rag" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    return $response
}

function Get-MemoryStats {
    $response = Invoke-RestMethod -Uri "$MemoryApiUrl/stats" -Method Get
    return $response
}

function Get-MemoryUsage {
    param([int]$Days = 7)
    
    $response = Invoke-RestMethod -Uri "$MemoryApiUrl/usage?days=$Days" -Method Get
    return $response
}
```

### Python Integration
Save as `skills/memory-system-integration/memory_client.py`:

```python
import requests
import json
from typing import List, Dict, Any

class MemoryClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def store(self, content: str, metadata: Dict = None, tags: List[str] = None) -> Dict:
        """Store a memory with embedding."""
        payload = {
            "content": content,
            "metadata": metadata or {},
            "tags": tags or []
        }
        response = requests.post(f"{self.base_url}/memories", json=payload)
        response.raise_for_status()
        return response.json()
    
    def retrieve(self, query: str, top_k: int = 5, filters: Dict = None) -> List[Dict]:
        """Retrieve similar memories."""
        payload = {
            "query": query,
            "top_k": top_k,
            "filters": filters or {},
            "use_cache": True
        }
        response = requests.post(f"{self.base_url}/memories/retrieve", json=payload)
        response.raise_for_status()
        return response.json()
    
    def ask(self, question: str, top_k: int = 5, max_tokens: int = 500) -> Dict:
        """Ask a question using RAG."""
        payload = {
            "question": question,
            "top_k": top_k,
            "max_tokens": max_tokens,
            "use_local": True
        }
        response = requests.post(f"{self.base_url}/rag", json=payload)
        response.raise_for_status()
        return response.json()
    
    def stats(self) -> Dict:
        """Get system statistics."""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()
    
    def usage(self, days: int = 7) -> Dict:
        """Get usage statistics."""
        response = requests.get(f"{self.base_url}/usage", params={"days": days})
        response.raise_for_status()
        return response.json()
```

## 🧠 Integration Patterns

### 1. Daily Learning Capture
```powershell
# At the end of each day, capture key learnings
$learnings = @"
Today's key learnings:
1. Fixed execution paralysis with time-boxing framework
2. Created mdsearch-pro as Windows-native alternative to qmd
3. Built production-ready local memory system with RAG
4. Successfully deployed 4 critical fixes in 45 minutes
"@

Store-Memory -Content $learnings -Tags @("daily", "learnings", "execution") -Metadata @{
    date = (Get-Date -Format "yyyy-MM-dd")
    type = "daily_summary"
}
```

### 2. Context Retrieval Before Tasks
```powershell
# Before starting a task, retrieve relevant context
function Get-RelevantContext {
    param([string]$TaskDescription)
    
    $context = Query-Memory -Query $TaskDescription -TopK 3
    $formatted = $context | ForEach-Object {
        "Previous learning: $($_.content) (relevance: $([math]::Round($_.similarity, 2)))"
    } | Join-String -Separator "`n"
    
    return $formatted
}

# Usage:
$context = Get-RelevantContext "Windows compatibility issues with Node.js tools"
Write-Host "Relevant context found:`n$context"
```

### 3. Decision Logging
```powershell
# Log important decisions with reasoning
function Log-Decision {
    param(
        [string]$Decision,
        [string]$Reasoning,
        [string[]]$Tags = @()
    )
    
    $content = "Decision: $Decision`nReasoning: $Reasoning"
    
    Store-Memory -Content $content -Tags ($Tags + "decision") -Metadata @{
        timestamp = (Get-Date -Format "o")
        type = "decision_log"
    }
}

# Usage:
Log-Decision `
    -Decision "Build Windows-native PowerShell alternative instead of fixing qmd" `
    -Reasoning "qmd has Bun dependency and /bin/sh errors on Windows. Building native PowerShell tool is faster and more reliable." `
    -Tags @("windows", "tooling", "decision")
```

### 4. RAG for Agent Self-Reflection
```powershell
# Ask the memory system about past work
function Reflect-On-Topic {
    param([string]$Topic)
    
    $response = Ask-WithContext -Question "What have I learned about $Topic?" -TopK 5
    return @{
        Answer = $response.answer
        Sources = $response.sources
        TokensUsed = $response.tokens_used
        Cost = $response.cost
    }
}

# Usage:
$reflection = Reflect-On-Topic "execution paralysis"
Write-Host "Reflection: $($reflection.Answer)"
```

## 🔗 Integration with Existing Skills

### ByteRover Integration
```powershell
# Store ByteRover search contexts in memory system
function Store-ByteRoverContext {
    param(
        [string]$Query,
        [string]$Context,
        [hashtable]$Metadata = @{}
    )
    
    $content = "ByteRover context for query: $Query`n`n$Context"
    
    Store-Memory -Content $content -Tags @("byterover", "context") -Metadata ($Metadata + @{
        source = "byterover"
        query = $Query
    })
}
```

### mdsearch-pro Integration
```powershell
# Complement text search with vector search
function Hybrid-Search {
    param(
        [string]$Query,
        [int]$VectorResults = 3,
        [int]$TextResults = 3
    )
    
    # Vector search (semantic)
    $vectorResults = Query-Memory -Query $Query -TopK $VectorResults
    
    # Text search (keyword) - using mdsearch-pro
    $textResults = & "$PSScriptRoot\..\mdsearch-pro\mdsearch-pro-final.ps1" -Search $Query -Limit $TextResults
    
    return @{
        VectorResults = $vectorResults
        TextResults = $textResults
    }
}
```

### Desktop Control Integration
```powershell
# Store automation patterns
function Store-AutomationPattern {
    param(
        [string]$Application,
        [string]$Pattern,
        [string]$Description
    )
    
    $content = "Automation pattern for $Application:`n$Pattern`n`nDescription: $Description"
    
    Store-Memory -Content $content -Tags @("automation", "desktop-control", $Application) -Metadata @{
        type = "automation_pattern"
        application = $Application
    }
}
```

## 📊 Health Checking

### System Health Check
```powershell
function Test-MemorySystem {
    try {
        # Test connection
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
        
        if ($health.status -eq "healthy") {
            Write-Host "✅ Memory system is healthy" -ForegroundColor Green
            Write-Host "   Database: $($health.database)"
            Write-Host "   Ollama: $($health.ollama)"
            return $true
        } else {
            Write-Host "⚠️  Memory system is degraded: $($health.status)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Memory system is unavailable: $_" -ForegroundColor Red
        return $false
    }
}
```

### Integration Health Check
```powershell
function Test-Integration {
    $tests = @()
    
    # Test 1: System health
    $tests += Test-MemorySystem
    
    # Test 2: Store capability
    try {
        $testMemory = Store-Memory -Content "Integration test memory" -Tags @("test")
        $tests += $true
    } catch {
        $tests += $false
    }
    
    # Test 3: Retrieve capability
    try {
        $results = Query-Memory -Query "test" -TopK 1
        $tests += $true
    } catch {
        $tests += $false
    }
    
    $passed = ($tests | Where-Object { $_ -eq $true }).Count
    $total = $tests.Count
    
    Write-Host "Integration test: $passed/$total passed" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
    return $passed -eq $total
}
```

## 🚀 Deployment Script

### Setup Memory System
```powershell
# deploy-memory-system.ps1
Write-Host "🚀 Deploying Local Memory System..." -ForegroundColor Cyan

# 1. Start Docker services
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
docker-compose -f "$PSScriptRoot\..\..\docker-compose.yml" up -d

# 2. Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 3. Pull Ollama models
Write-Host "Pulling Ollama models..." -ForegroundColor Yellow
docker exec memory_ollama ollama pull nomic-embed-text
docker exec memory_ollama ollama pull llama3.2:3b

# 4. Test the system
Write-Host "Testing memory system..." -ForegroundColor Yellow
if (Test-MemorySystem) {
    Write-Host "✅ Memory system deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Memory system deployment failed" -ForegroundColor Red
}
```

## 📈 Usage Examples

### Example 1: Daily Workflow
```powershell
# Morning: Retrieve context for today's work
$context = Get-RelevantContext "today's priorities execution framework"
Write-Host "Today's context:`n$context"

# During work: Log decisions
Log-Decision -Decision "Use PowerShell for Windows automation" -Reasoning "Cross-platform tools have compatibility issues on Windows"

# Evening: Store learnings
$learnings = @"
Today I:
1. Deployed memory system successfully
2. Created integration skill
3. Tested all components
"@
Store-Memory -Content $learnings -Tags @("daily", "2026-03-31")
```

### Example 2: Debugging Support
```powershell
# When encountering an error, search for similar past solutions
function Find-PastSolutions {
    param([string]$ErrorDescription)
    
    $solutions = Query-Memory -Query $ErrorDescription -TopK 3 -Filters @{tags = "solution"}
    
    if ($solutions) {
        Write-Host "Found $(@($solutions).Count) past solutions:" -ForegroundColor Green
        $solutions | ForEach-Object {
            Write-Host "  • $($_.content)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "No past solutions found. Consider adding one after solving." -ForegroundColor Yellow
    }
}
```

### Example 3: Project Context Management
```powershell
# Store project-specific context
function Set-ProjectContext {
    param([string]$ProjectName, [string]$Context)
    
    Store-Memory -Content $Context -Tags @("project", $ProjectName) -Metadata @{
        type = "project_context"
        project = $ProjectName
        timestamp = (Get-Date -Format "o")
    }
}

# Retrieve project context
function Get-ProjectContext {
    param([string]$ProjectName)
    
    $context = Query-Memory -Query $ProjectName -TopK 5 -Filters @{tags = "project"}
    return $context
}
```

## 🔒 Security Notes
- The memory system runs locally (no external API calls by default)
- All data stays on your machine
- No API keys required for local operation
- Budget enforcement prevents accidental spending if external APIs are enabled

## 📝 Best Practices
1. **Tag everything**: Use consistent tags for easy filtering
2. **Store metadata**: Include source, timestamp, type in metadata
3. **Regular consolidation**: Periodically review and merge similar memories
4. **Health checks**: Verify system is working before critical operations
5. **Fallback handling**: Gracefully degrade if memory system is unavailable

## 🆘 Troubleshooting

### Common Issues
1. **Service not responding**: Run `docker-compose ps` to check container status
2. **Models not loaded**: Run `docker exec memory_ollama ollama list` to verify models
3. **Database connection failed**: Check PostgreSQL logs with `docker logs memory_postgres`
4. **High memory usage**: Consider reducing model size or adding swap space

### Debug Commands
```powershell
# Check container status
docker-compose -f "$PSScriptRoot\..\..\docker-compose.yml" ps

# View logs
docker-compose -f "$PSScriptRoot\..\..\docker-compose.yml" logs

# Test API directly
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/tags
```

---

**Status**: Ready for integration | **Cost**: $0 local | **Storage**: PostgreSQL + pgvector | **AI Models**: Ollama (nomic-embed-text, llama3.2:3b)