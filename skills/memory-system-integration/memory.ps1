# Memory System Integration - PowerShell Module
# Usage: . .\memory.ps1

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
    
    try {
        $response = Invoke-RestMethod -Uri "$MemoryApiUrl/memories" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host "✅ Memory stored with ID: $($response.id)" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "❌ Failed to store memory: $_" -ForegroundColor Red
        return $null
    }
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
        use_cache = $true
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$MemoryApiUrl/memories/retrieve" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host "✅ Found $($response.Count) memories for query: '$Query'" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "❌ Failed to query memory: $_" -ForegroundColor Red
        return @()
    }
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
        use_local = $true
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$MemoryApiUrl/rag" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host "✅ RAG response generated ($($response.tokens_used) tokens, $$($response.cost))" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "❌ Failed to get RAG response: $_" -ForegroundColor Red
        return $null
    }
}

function Get-MemoryStats {
    try {
        $response = Invoke-RestMethod -Uri "$MemoryApiUrl/stats" -Method Get -ErrorAction Stop
        return $response
    } catch {
        Write-Host "❌ Failed to get memory stats: $_" -ForegroundColor Red
        return $null
    }
}

function Get-MemoryUsage {
    param([int]$Days = 7)
    
    try {
        $response = Invoke-RestMethod -Uri "$MemoryApiUrl/usage?days=$Days" -Method Get -ErrorAction Stop
        return $response
    } catch {
        Write-Host "❌ Failed to get memory usage: $_" -ForegroundColor Red
        return $null
    }
}

function Test-MemorySystem {
    try {
        # Test connection
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
        
        if ($health.status -eq "healthy") {
            Write-Host "✅ Memory system is healthy" -ForegroundColor Green
            Write-Host "   Database: $($health.database)" -ForegroundColor Gray
            Write-Host "   Ollama: $($health.ollama)" -ForegroundColor Gray
            return $true
        } else {
            Write-Host "⚠️  Memory system is degraded: $($health.status)" -ForegroundColor Yellow
            Write-Host "   Database: $($health.database)" -ForegroundColor Gray
            Write-Host "   Ollama: $($health.ollama)" -ForegroundColor Gray
            return $false
        }
    } catch {
        Write-Host "❌ Memory system is unavailable: $_" -ForegroundColor Red
        return $false
    }
}

function Get-RelevantContext {
    param([string]$TaskDescription)
    
    $context = Query-Memory -Query $TaskDescription -TopK 3
    if ($context.Count -eq 0) {
        return "No relevant context found for: $TaskDescription"
    }
    
    $formatted = $context | ForEach-Object {
        $similarity = [math]::Round($_.similarity, 2)
        "• $($_.content) (relevance: $similarity)"
    } | Join-String -Separator "`n"
    
    return "Relevant context for '$TaskDescription':`n$formatted"
}

function Log-Decision {
    param(
        [string]$Decision,
        [string]$Reasoning,
        [string[]]$Tags = @()
    )
    
    $content = "Decision: $Decision`nReasoning: $Reasoning"
    
    $result = Store-Memory -Content $content -Tags ($Tags + "decision") -Metadata @{
        timestamp = (Get-Date -Format "o")
        type = "decision_log"
    }
    
    return $result
}

function Reflect-On-Topic {
    param([string]$Topic)
    
    $response = Ask-WithContext -Question "What have I learned about $Topic?" -TopK 5
    if ($response) {
        return @{
            Answer = $response.answer
            Sources = $response.sources
            TokensUsed = $response.tokens_used
            Cost = $response.cost
        }
    }
    return $null
}

function Store-ByteRoverContext {
    param(
        [string]$Query,
        [string]$Context,
        [hashtable]$Metadata = @{}
    )
    
    $content = "ByteRover context for query: $Query`n`n$Context"
    
    $result = Store-Memory -Content $content -Tags @("byterover", "context") -Metadata ($Metadata + @{
        source = "byterover"
        query = $Query
        timestamp = (Get-Date -Format "o")
    })
    
    return $result
}

function Hybrid-Search {
    param(
        [string]$Query,
        [int]$VectorResults = 3,
        [int]$TextResults = 3
    )
    
    # Vector search (semantic)
    $vectorResults = Query-Memory -Query $Query -TopK $VectorResults
    
    # Text search (keyword) - using mdsearch-pro if available
    $textResults = @()
    $mdsearchPath = "$PSScriptRoot\..\mdsearch-pro\mdsearch-pro-final.ps1"
    if (Test-Path $mdsearchPath) {
        try {
            $textResults = & $mdsearchPath -Search $Query -Limit $TextResults
        } catch {
            Write-Host "⚠️  mdsearch-pro not available: $_" -ForegroundColor Yellow
        }
    }
    
    return @{
        VectorResults = $vectorResults
        TextResults = $textResults
    }
}

function Store-AutomationPattern {
    param(
        [string]$Application,
        [string]$Pattern,
        [string]$Description
    )
    
    $content = "Automation pattern for ${Application}:`n$Pattern`n`nDescription: $Description"
    
    $result = Store-Memory -Content $content -Tags @("automation", "desktop-control", $Application) -Metadata @{
        type = "automation_pattern"
        application = $Application
        timestamp = (Get-Date -Format "o")
    }
    
    return $result
}

function Set-ProjectContext {
    param([string]$ProjectName, [string]$Context)
    
    $result = Store-Memory -Content $Context -Tags @("project", $ProjectName) -Metadata @{
        type = "project_context"
        project = $ProjectName
        timestamp = (Get-Date -Format "o")
    }
    
    return $result
}

function Get-ProjectContext {
    param([string]$ProjectName)
    
    $context = Query-Memory -Query $ProjectName -TopK 5 -Filters @{tags = "project"}
    return $context
}

function Find-PastSolutions {
    param([string]$ErrorDescription)
    
    $solutions = Query-Memory -Query $ErrorDescription -TopK 3 -Filters @{tags = "solution"}
    
    if ($solutions.Count -gt 0) {
        Write-Host "Found $($solutions.Count) past solutions:" -ForegroundColor Green
        $solutions | ForEach-Object {
            Write-Host "  • $($_.content)" -ForegroundColor Yellow
        }
        return $solutions
    } else {
        Write-Host "No past solutions found. Consider adding one after solving." -ForegroundColor Yellow
        return @()
    }
}

function Test-Integration {
    $tests = @()
    
    # Test 1: System health
    Write-Host "Testing memory system health..." -ForegroundColor Cyan
    $tests += Test-MemorySystem
    
    # Test 2: Store capability
    Write-Host "Testing store capability..." -ForegroundColor Cyan
    try {
        $testMemory = Store-Memory -Content "Integration test memory $(Get-Date -Format 'HH:mm:ss')" -Tags @("test")
        $tests += ($testMemory -ne $null)
    } catch {
        $tests += $false
    }
    
    # Test 3: Retrieve capability
    Write-Host "Testing retrieve capability..." -ForegroundColor Cyan
    try {
        $results = Query-Memory -Query "test" -TopK 1
        $tests += ($results.Count -gt 0)
    } catch {
        $tests += $false
    }
    
    $passed = ($tests | Where-Object { $_ -eq $true }).Count
    $total = $tests.Count
    
    if ($passed -eq $total) {
        Write-Host "✅ Integration test: $passed/$total passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Integration test: $passed/$total passed" -ForegroundColor Yellow
    }
    
    return $passed -eq $total
}

# Export functions
Export-ModuleMember -Function *
Write-Host "Memory System Integration module loaded. Available functions:" -ForegroundColor Cyan
Write-Host "  • Store-Memory, Query-Memory, Ask-WithContext" -ForegroundColor Gray
Write-Host "  • Get-MemoryStats, Get-MemoryUsage, Test-MemorySystem" -ForegroundColor Gray
Write-Host "  • Get-RelevantContext, Log-Decision, Reflect-On-Topic" -ForegroundColor Gray
Write-Host "  • Hybrid-Search, Find-PastSolutions, Test-Integration" -ForegroundColor Gray