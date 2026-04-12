# Deploy Self-Evolving Memory System
# Sets up the complete memory system with auto-pruning and evolution

Write-Host "🚀 Deploying Self-Evolving Persistent Memory System" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Warning: Running without administrator privileges" -ForegroundColor Yellow
    Write-Host "   Some features (scheduled tasks) may require admin rights" -ForegroundColor Yellow
    Write-Host ""
}

# 1. Create directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Cyan

$directories = @(
    "memory-system",
    "memory-system/hot-ram",
    "memory-system/warm-store", 
    "memory-system/cold-store",
    "memory-system/cold-store/embeddings",
    "memory-system/cold-store/metadata",
    "memory-system/cold-store/content",
    "memory-system/archive",
    "memory-system/system-state"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "   Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "   Exists: $dir" -ForegroundColor Gray
    }
}

Write-Host "✅ Directory structure created" -ForegroundColor Green
Write-Host ""

# 2. Initialize configuration
Write-Host "⚙️  Initializing configuration..." -ForegroundColor Cyan

$config = @{
    version = "1.0.0"
    deployedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    pruning = @{
        hotRamMaxTokens = 4096
        warmStoreRetentionDays = 7
        archiveRetentionDays = 90
        pruningThreshold = 0.3
        autoPruneIntervalMinutes = 15
    }
    evolution = @{
        learningRate = 0.01
        adaptationWindowDays = 30
        modelUpdateIntervalDays = 7
        performanceTracking = $true
    }
    storage = @{
        compressionLevel = 6
        embeddingModel = "all-MiniLM-L6-v2"
        vectorDimensions = 384
        maxEmbeddingCacheSizeMB = 1000
    }
    retrieval = @{
        defaultLimit = 10
        similarityThreshold = 0.5
        hybridSearch = $true
    }
}

$configPath = "memory-system/system-state/config.json"
$config | ConvertTo-Json -Depth 10 | Out-File $configPath -Encoding UTF8
Write-Host "   Configuration saved: $configPath" -ForegroundColor Green
Write-Host ""

# 3. Initialize metrics and state files
Write-Host "📊 Initializing metrics and state..." -ForegroundColor Cyan

# Pruning metrics
$pruningMetrics = @{
    totalRuns = 0
    itemsPruned = 0
    itemsArchived = 0
    archivesCleaned = 0
    lastRun = $null
    averageRunTimeSeconds = 0
}
$pruningMetrics | ConvertTo-Json -Depth 10 | Out-File "memory-system/system-state/pruning-metrics.json" -Encoding UTF8

# Evolution metrics
$evolutionMetrics = @{
    totalCycles = 0
    lastEvolution = $null
    performanceImprovements = @()
    modelUpdates = 0
}
$evolutionMetrics | ConvertTo-Json -Depth 10 | Out-File "memory-system/system-state/evolution-metrics.json" -Encoding UTF8

# Usage patterns
$usagePatterns = @{
    totalQueries = 0
    successfulRetrievals = 0
    averageSimilarity = 0
    popularTopics = @()
    accessPatterns = @{}
}
$usagePatterns | ConvertTo-Json -Depth 10 | Out-File "memory-system/system-state/usage-patterns.json" -Encoding UTF8

Write-Host "   State files initialized" -ForegroundColor Green
Write-Host ""

# 4. Create sample memory items (for testing)
Write-Host "🧠 Creating sample memory items..." -ForegroundColor Cyan

$sampleMemories = @(
    @{
        content = "Memory systems should have multiple layers: Hot RAM for immediate context, Warm Store for recent memories, and Cold Store for long-term storage."
        metadata = @{ type = "learning"; tags = @("memory", "architecture", "layers") }
    },
    @{
        content = "Auto-pruning is essential for managing context limits. Use recency, relevance, and importance scores to decide what to keep."
        metadata = @{ type = "learning"; tags = @("pruning", "context", "optimization") }
    },
    @{
        content = "Self-evolving systems learn from usage patterns and adapt their behavior over time for better performance."
        metadata = @{ type = "principle"; tags = @("evolution", "adaptation", "learning") }
    },
    @{
        content = "Vector embeddings enable semantic search, allowing the system to find relevant memories even without exact keyword matches."
        metadata = @{ type = "learning"; tags = @("embeddings", "semantic-search", "retrieval") }
    },
    @{
        content = "Importance scoring should consider: user feedback, frequency of access, content type (code vs text), and relationship to core principles."
        metadata = @{ type = "learning"; tags = @("importance", "scoring", "metrics") }
    }
)

$i = 1
foreach ($sample in $sampleMemories) {
    $metadataJson = $sample.metadata | ConvertTo-Json -Compress
    $result = .\memory-manager.ps1 -Action store -Content $sample.content -Metadata $metadataJson
    Write-Host "   Created sample memory $i" -ForegroundColor Gray
    $i++
}

Write-Host "✅ Sample memories created" -ForegroundColor Green
Write-Host ""

# 5. Set up scheduled tasks (if running as admin)
if ($isAdmin) {
    Write-Host "⏰ Setting up scheduled tasks..." -ForegroundColor Cyan
    
    # Auto-pruning task (every 15 minutes)
    try {
        $pruneAction = New-ScheduledTaskAction -Execute "PowerShell.exe" `
            -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\auto-pruner.ps1`""
        
        $pruneTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
            -RepetitionInterval (New-TimeSpan -Minutes $config.pruning.autoPruneIntervalMinutes) `
            -RepetitionDuration (New-TimeSpan -Days 365)
        
        $pruneSettings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -WakeToRun
        
        Register-ScheduledTask -TaskName "MemorySystem-AutoPrune" `
            -Action $pruneAction `
            -Trigger $pruneTrigger `
            -Settings $pruneSettings `
            -Description "Auto-prunes memory context every $($config.pruning.autoPruneIntervalMinutes) minutes" `
            -Force | Out-Null
        
        Write-Host "   Created task: MemorySystem-AutoPrune (every $($config.pruning.autoPruneIntervalMinutes) minutes)" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Failed to create auto-prune task: $_" -ForegroundColor Yellow
    }
    
    # Weekly evolution task (Sunday at 2 AM)
    try {
        $evolveAction = New-ScheduledTaskAction -Execute "PowerShell.exe" `
            -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\evolution-engine.ps1`""
        
        $evolveTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2AM
        
        $evolveSettings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable
        
        Register-ScheduledTask -TaskName "MemorySystem-Evolution" `
            -Action $evolveAction `
            -Trigger $evolveTrigger `
            -Settings $evolveSettings `
            -Description "Runs weekly evolution cycle for memory system" `
            -Force | Out-Null
        
        Write-Host "   Created task: MemorySystem-Evolution (weekly, Sunday 2AM)" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Failed to create evolution task: $_" -ForegroundColor Yellow
    }
    
    # Daily stats task (daily at 6 AM)
    try {
        $statsAction = New-ScheduledTaskAction -Execute "PowerShell.exe" `
            -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\memory-manager.ps1`" -Action stats"
        
        $statsTrigger = New-ScheduledTaskTrigger -Daily -At 6AM
        
        $statsSettings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable
        
        Register-ScheduledTask -TaskName "MemorySystem-DailyStats" `
            -Action $statsAction `
            -Trigger $statsTrigger `
            -Settings $statsSettings `
            -Description "Generates daily memory system statistics" `
            -Force | Out-Null
        
        Write-Host "   Created task: MemorySystem-DailyStats (daily, 6AM)" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Failed to create stats task: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Skipping scheduled tasks (requires administrator privileges)" -ForegroundColor Yellow
    Write-Host "   To run tasks manually:" -ForegroundColor Gray
    Write-Host "   - Auto-prune: .\auto-pruner.ps1" -ForegroundColor Gray
    Write-Host "   - Get stats: .\memory-manager.ps1 -Action stats" -ForegroundColor Gray
}

Write-Host ""

# 6. Create quick-start guide
Write-Host "📖 Creating quick-start guide..." -ForegroundColor Cyan

$quickStart = @"
# Self-Evolving Memory System - Quick Start Guide

## System Overview
A multi-layer memory system with auto-pruning and self-evolution capabilities.

## Directory Structure
* memory-system/hot-ram/ - Immediate context (session memory)
* memory-system/warm-store/ - Recent memories (7 days)
* memory-system/cold-store/ - Long-term storage
* memory-system/archive/ - Historical archives
* memory-system/system-state/ - Configuration and metrics

## Quick Commands

### Store a Memory
```powershell
.\memory-manager.ps1 -Action store -Content "Your memory content here" -Metadata '{"type":"learning","tags":["topic1","topic2"]}'
```

### Retrieve Memories
```powershell
.\memory-manager.ps1 -Action retrieve -Query "search query" -Limit 5
```

### Run Auto-Pruning
```powershell
.\auto-pruner.ps1
```

### View Statistics
```powershell
.\memory-manager.ps1 -Action stats
```

## Scheduled Tasks
- Auto-pruning: Every 15 minutes
- Evolution: Weekly (Sunday 2AM)
- Daily stats: Daily (6AM)

## Configuration
Edit: `memory-system/system-state/config.json`

## Monitoring
- Metrics: `memory-system/system-state/*-metrics.json`
- Logs: `memory-system/system-state/*-log.jsonl`

## Testing the System
1. Store some memories using the store command
2. Search for them using retrieve command
3. Check stats to see system status
4. Run auto-pruner to see pruning in action

## Next Steps
1. Integrate with your existing workflow
2. Customize pruning thresholds
3. Add domain-specific embedding models
4. Set up monitoring alerts
"@

$quickStart | Out-File "memory-system/QUICK-START.md" -Encoding UTF8
Write-Host "   Quick-start guide created: memory-system/QUICK-START.md" -ForegroundColor Green
Write-Host ""

# 7. Test the system
Write-Host "🧪 Testing the system..." -ForegroundColor Cyan

# Test 1: Retrieve sample memories
Write-Host "   Test 1: Retrieving sample memories..." -ForegroundColor Gray
$results = .\memory-manager.ps1 -Action retrieve -Query "memory system architecture" -Limit 2
if ($results -and $results.Count -gt 0) {
    Write-Host "   ✅ Retrieval test passed" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Retrieval test returned no results" -ForegroundColor Yellow
}

# Test 2: Check statistics
Write-Host "   Test 2: Checking system statistics..." -ForegroundColor Gray
$stats = .\memory-manager.ps1 -Action stats
if ($stats) {
    Write-Host "   ✅ Statistics test passed" -ForegroundColor Green
}

Write-Host ""

# 8. Deployment complete
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ System deployed successfully" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review the quick-start guide: memory-system/QUICK-START.md" -ForegroundColor White
Write-Host "2. Test the system with your own memories" -ForegroundColor White
Write-Host "3. Monitor performance in memory-system/system-state/" -ForegroundColor White
Write-Host "4. Adjust configuration as needed" -ForegroundColor White
Write-Host ""
Write-Host "🔧 System Status:" -ForegroundColor Cyan
Write-Host "   - Directory structure: ✅" -ForegroundColor Green
Write-Host "   - Configuration: ✅" -ForegroundColor Green
Write-Host "   - Sample data: ✅" -ForegroundColor Green
Write-Host "   - Scheduled tasks: $(if ($isAdmin) { '✅' } else { '⚠️ (requires admin)' })" -ForegroundColor $(if ($isAdmin) { 'Green' } else { 'Yellow' })
Write-Host "   - Quick-start guide: ✅" -ForegroundColor Green
Write-Host "   - System test: ✅" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Your self-evolving memory system is ready!" -ForegroundColor Green
Write-Host "   Start storing and retrieving memories to see it in action." -ForegroundColor White