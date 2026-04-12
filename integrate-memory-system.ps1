# Memory System Integration
# Shows how to integrate the self-evolving memory system into daily workflow

Write-Host "🔗 Integrating Memory System into Workflow" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check if system is deployed
Write-Host "1. Checking system status..." -ForegroundColor Yellow

if (-not (Test-Path "memory-system")) {
    Write-Host "   ❌ Memory system not deployed" -ForegroundColor Red
    Write-Host "   Run: .\deploy-memory-system.ps1" -ForegroundColor White
    exit 1
}

if (-not (Test-Path "memory-manager.ps1")) {
    Write-Host "   ❌ Memory manager not found" -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ Memory system is deployed" -ForegroundColor Green
Write-Host ""

# 2. Show basic usage examples
Write-Host "2. Basic Usage Examples" -ForegroundColor Yellow
Write-Host ""

Write-Host "   📝 Storing Learnings:" -ForegroundColor Cyan
Write-Host '   .\memory-manager.ps1 -Action store -Content "Learned that auto-pruning improves context management" -Metadata ''{"type":"learning","tags":["pruning","context"]}''' -ForegroundColor Gray
Write-Host ""

Write-Host "   🔍 Retrieving Knowledge:" -ForegroundColor Cyan
Write-Host '   .\memory-manager.ps1 -Action retrieve -Query "how to manage context limits" -Limit 3' -ForegroundColor Gray
Write-Host ""

Write-Host "   📊 Checking System Health:" -ForegroundColor Cyan
Write-Host '   .\memory-manager.ps1 -Action stats' -ForegroundColor Gray
Write-Host ""

# 3. Create workflow integration functions
Write-Host "3. Workflow Integration Functions" -ForegroundColor Yellow

$integrationScript = @"
# Memory System Integration Functions
# Add these to your PowerShell profile or workflow scripts

function Store-Learning {
    param(
        [Parameter(Mandatory=`$true)]
        [string]`$Content,
        
        [string[]]`$Tags = @(),
        
        [ValidateSet("learning", "decision", "code", "reference")]
        [string]`$Type = "learning",
        
        [bool]`$Important = `$false
    )
    
    `$metadata = @{
        type = `$Type
        tags = `$Tags
        userFlagged = `$Important
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
    
    `$metadataJson = `$metadata | ConvertTo-Json -Compress
    
    Write-Host "💾 Storing learning..." -ForegroundColor Cyan
    .\memory-manager.ps1 -Action store -Content `$Content -Metadata `$metadataJson
    
    # Also log to daily memory file
    `$dailyFile = "memory/`$(Get-Date -Format 'yyyy-MM-dd').md"
    if (-not (Test-Path `$dailyFile)) {
        "## `$(Get-Date -Format 'yyyy-MM-dd')`n`n" | Out-File `$dailyFile -Encoding UTF8
    }
    
    "### Learning at `$(Get-Date -Format 'HH:mm:ss')`n`$Content`n`n" | Out-File `$dailyFile -Append -Encoding UTF8
}

function Search-Memories {
    param(
        [Parameter(Mandatory=`$true)]
        [string]`$Query,
        
        [int]`$Limit = 5
    )
    
    Write-Host "🔍 Searching memories for: '`$Query'" -ForegroundColor Cyan
    `$results = .\memory-manager.ps1 -Action retrieve -Query `$Query -Limit `$Limit
    
    return `$results
}

function Get-Memory-Stats {
    Write-Host "📊 Memory System Statistics" -ForegroundColor Cyan
    .\memory-manager.ps1 -Action stats
}

function Run-Memory-Maintenance {
    Write-Host "🛠️  Running memory maintenance..." -ForegroundColor Cyan
    .\auto-pruner.ps1
}

function Start-Memory-Session {
    param([string]`$Context)
    
    Write-Host "🧠 Starting memory-assisted session" -ForegroundColor Green
    Write-Host "   Context: `$Context" -ForegroundColor Gray
    
    # Load relevant memories for this context
    `$relevantMemories = Search-Memories -Query `$Context -Limit 3
    
    if (`$relevantMemories -and `$relevantMemories.Count -gt 0) {
        Write-Host "   Found `$(`$relevantMemories.Count) relevant memories" -ForegroundColor Green
        return `$relevantMemories
    } else {
        Write-Host "   No relevant memories found" -ForegroundColor Yellow
        return @()
    }
}

# Add to PowerShell profile
function Add-To-Profile {
    `$profileContent = Get-Content `$PROFILE -ErrorAction SilentlyContinue
    `$integrationContent = Get-Content "integrate-memory-system.ps1" | Select-Object -Skip 1
    
    if (`$profileContent -notmatch "Store-Learning") {
        "`n# Memory System Integration`n" | Out-File `$PROFILE -Append -Encoding UTF8
        `$integrationContent | Out-File `$PROFILE -Append -Encoding UTF8
        Write-Host "✅ Added memory functions to PowerShell profile" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Memory functions already in profile" -ForegroundColor Yellow
    }
}
"@

$integrationScript | Out-File "memory-system-integration.ps1" -Encoding UTF8
Write-Host "   Created integration script: memory-system-integration.ps1" -ForegroundColor Green
Write-Host ""

# 4. Create sample workflow
Write-Host "4. Sample Workflow" -ForegroundColor Yellow

$sampleWorkflow = @"
# Sample Daily Workflow with Memory System

## Morning Routine
1. **Start memory-assisted session**
```powershell
Start-Memory-Session -Context "daily planning"
```

2. **Store yesterday's learnings**
```powershell
Store-Learning -Content "Completed trading system UI optimizations" -Tags @("trading", "ui", "optimization") -Type learning
Store-Learning -Content "Fixed Angular compilation errors by removing unused imports" -Tags @("angular", "debugging", "typescript") -Type learning -Important `$true
```

## During Work
1. **Before starting a task, search for relevant knowledge**
```powershell
Search-Memories -Query "Angular error handling" -Limit 3
```

2. **When you learn something new, store it immediately**
```powershell
Store-Learning -Content "WebSocket connections need heartbeat to stay alive" -Tags @("websocket", "networking") -Type learning
```

3. **When making decisions, store the reasoning**
```powershell
Store-Learning -Content "Chose PostgreSQL over MongoDB for better transaction support" -Tags @("database", "decision", "architecture") -Type decision -Important `$true
```

## Evening Routine
1. **Review and consolidate learnings**
```powershell
Search-Memories -Query "today's learnings" -Limit 10
```

2. **Run maintenance**
```powershell
Run-Memory-Maintenance
```

3. **Check system health**
```powershell
Get-Memory-Stats
```

## Weekly Routine (Sunday)
1. **Let evolution engine run automatically (scheduled task)**
2. **Review evolution report**
```powershell
Get-Content "memory-system/system-state/evolution-report-*.json" | ConvertFrom-Json | Format-List
```

## Integration with Existing Tools
1. **Add to PowerShell profile for global access**
```powershell
. .\memory-system-integration.ps1
Add-To-Profile
```

2. **Create aliases for frequent commands**
```powershell
New-Alias -Name remember -Value Store-Learning
New-Alias -Name recall -Value Search-Memories
New-Alias -Name memstats -Value Get-Memory-Stats
```

3. **Use in scripts and automation**
```powershell
# In your automation scripts:
`$solution = Search-Memories -Query "git large file error" -Limit 1
if (`$solution) {
    Write-Host "Found solution: `$(`$solution.Content)"
}
```
"@

$sampleWorkflow | Out-File "memory-system-workflow.md" -Encoding UTF8
Write-Host "   Created sample workflow: memory-system-workflow.md" -ForegroundColor Green
Write-Host ""

# 5. Test integration
Write-Host "5. Testing Integration" -ForegroundColor Yellow

Write-Host "   Testing memory storage..." -ForegroundColor Gray
$testContent = "Integration test: Memory system can be easily integrated into daily workflow"
$testMetadata = '{"type":"test","tags":["integration","workflow"]}'
.\memory-manager.ps1 -Action store -Content $testContent -Metadata $testMetadata

Write-Host ""
Write-Host "   Testing memory retrieval..." -ForegroundColor Gray
.\memory-manager.ps1 -Action retrieve -Query "workflow integration" -Limit 2

Write-Host ""
Write-Host "   Testing statistics..." -ForegroundColor Gray
.\memory-manager.ps1 -Action stats

Write-Host ""

# 6. Summary
Write-Host "✅ Integration Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Created Resources:" -ForegroundColor Cyan
Write-Host "   - memory-system-integration.ps1 (PowerShell functions)" -ForegroundColor White
Write-Host "   - memory-system-workflow.md (Sample workflow)" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review memory-system-integration.ps1" -ForegroundColor White
Write-Host "   2. Add functions to your PowerShell profile" -ForegroundColor White
Write-Host "   3. Follow the sample workflow for a day" -ForegroundColor White
Write-Host "   4. Customize based on your needs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Pro Tips:" -ForegroundColor Cyan
Write-Host "   - Store learnings immediately after discovering them" -ForegroundColor White
Write-Host "   - Search before starting new tasks" -ForegroundColor White
Write-Host "   - Flag important decisions with -Important `$true" -ForegroundColor White
Write-Host "   - Let the auto-pruner handle context management" -ForegroundColor White
Write-Host "   - Review evolution reports weekly" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Your self-evolving memory system is now ready for integration!" -ForegroundColor Green
Write-Host "   Start using it today to enhance your productivity and knowledge retention." -ForegroundColor White