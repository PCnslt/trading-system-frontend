# Evolution Engine - Self-Evolving Memory System
# Implements learning and adaptation based on usage patterns

Write-Host "🧬 Starting Evolution Engine" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

# Load configuration
$configPath = "memory-system/system-state/config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
} else {
    Write-Host "❌ Configuration not found" -ForegroundColor Red
    exit 1
}

# Load metrics
$pruningMetricsPath = "memory-system/system-state/pruning-metrics.json"
$evolutionMetricsPath = "memory-system/system-state/evolution-metrics.json"
$usagePatternsPath = "memory-system/system-state/usage-patterns.json"

function Load-Metrics {
    $metrics = @{}
    
    if (Test-Path $pruningMetricsPath) {
        $metrics.pruning = Get-Content $pruningMetricsPath | ConvertFrom-Json
    }
    
    if (Test-Path $evolutionMetricsPath) {
        $metrics.evolution = Get-Content $evolutionMetricsPath | ConvertFrom-Json
    }
    
    if (Test-Path $usagePatternsPath) {
        $metrics.usage = Get-Content $usagePatternsPath | ConvertFrom-Json
    }
    
    return $metrics
}

function Analyze-Performance {
    param([hashtable]$Metrics)
    
    Write-Host "📈 Analyzing system performance..." -ForegroundColor Yellow
    
    $analysis = @{
        retrievalEffectiveness = 0.0
        pruningEfficiency = 0.0
        storageOptimization = 0.0
        adaptationNeeded = $false
        recommendations = @()
    }
    
    # Analyze retrieval effectiveness
    if ($metrics.usage -and $metrics.usage.totalQueries -gt 0) {
        $analysis.retrievalEffectiveness = $metrics.usage.successfulRetrievals / $metrics.usage.totalQueries
        if ($analysis.retrievalEffectiveness -lt 0.7) {
            $analysis.adaptationNeeded = $true
            $analysis.recommendations += "Improve retrieval accuracy (currently: $($analysis.retrievalEffectiveness.ToString('P1')))"
        }
    }
    
    # Analyze pruning efficiency
    if ($metrics.pruning -and $metrics.pruning.totalRuns -gt 0) {
        $totalProcessed = $metrics.pruning.itemsPruned + $metrics.pruning.itemsArchived
        if ($totalProcessed -gt 0) {
            $analysis.pruningEfficiency = $metrics.pruning.itemsArchived / $totalProcessed
            if ($analysis.pruningEfficiency -lt 0.6) {
                $analysis.recommendations += "Optimize pruning thresholds (efficiency: $($analysis.pruningEfficiency.ToString('P1')))"
            }
        }
    }
    
    # Check storage distribution
    $hotRamCount = (Get-ChildItem "memory-system/hot-ram" -Filter "*.json" -ErrorAction SilentlyContinue).Count
    $warmStoreCount = (Get-ChildItem "memory-system/warm-store" -Filter "*.json" -ErrorAction SilentlyContinue).Count
    $coldStoreCount = (Get-ChildItem "memory-system/cold-store/content" -Filter "*.json" -ErrorAction SilentlyContinue).Count
    
    $totalItems = $hotRamCount + $warmStoreCount + $coldStoreCount
    if ($totalItems -gt 0) {
        $coldStoreRatio = $coldStoreCount / $totalItems
        $analysis.storageOptimization = $coldStoreRatio
        
        if ($coldStoreRatio -lt 0.2 -and $totalItems -gt 50) {
            $analysis.recommendations += "Increase cold store utilization (currently: $($coldStoreRatio.ToString('P1')))"
        }
    }
    
    return $analysis
}

function Optimize-PruningThresholds {
    param(
        [hashtable]$Metrics,
        [hashtable]$Analysis
    )
    
    Write-Host "⚙️  Optimizing pruning thresholds..." -ForegroundColor Yellow
    
    $currentThreshold = $config.pruning.pruningThreshold
    $newThreshold = $currentThreshold
    
    # Adjust based on pruning efficiency
    if ($analysis.pruningEfficiency -lt 0.6) {
        # Too aggressive pruning - lower threshold to keep more
        $newThreshold = [Math]::Max(0.2, $currentThreshold - 0.05)
        Write-Host "   Lowering threshold from $currentThreshold to $newThreshold (pruning too aggressive)" -ForegroundColor Blue
    } elseif ($analysis.pruningEfficiency -gt 0.8) {
        # Too conservative pruning - raise threshold to prune more
        $newThreshold = [Math]::Min(0.5, $currentThreshold + 0.05)
        Write-Host "   Raising threshold from $currentThreshold to $newThreshold (pruning too conservative)" -ForegroundColor Blue
    } else {
        Write-Host "   Threshold optimal at $currentThreshold" -ForegroundColor Green
    }
    
    # Update configuration if changed
    if ($newThreshold -ne $currentThreshold) {
        $config.pruning.pruningThreshold = $newThreshold
        $config | ConvertTo-Json -Depth 10 | Out-File $configPath -Encoding UTF8
        Write-Host "   Updated pruning threshold to $newThreshold" -ForegroundColor Green
    }
}

function Optimize-StorageTiers {
    param([hashtable]$Analysis)
    
    Write-Host "💾 Optimizing storage tiers..." -ForegroundColor Yellow
    
    # Check if we need to migrate items between tiers
    $hotRamPath = "memory-system/hot-ram"
    $warmStorePath = "memory-system/warm-store"
    $coldStorePath = "memory-system/cold-store/content"
    
    # Migrate important items from warm store to cold store
    if (Test-Path $warmStorePath) {
        $migratedCount = 0
        Get-ChildItem $warmStorePath -Filter "*.json" | ForEach-Object {
            $item = Get-Content $_.FullName | ConvertFrom-Json
            
            # Migrate if importance > 0.8 and accessed multiple times
            if ($item.importance -gt 0.8 -and $item.accessCount -gt 3) {
                if (-not (Test-Path $coldStorePath)) {
                    New-Item -ItemType Directory -Force -Path $coldStorePath | Out-Null
                }
                
                Copy-Item $_.FullName (Join-Path $coldStorePath $_.Name)
                Remove-Item $_.FullName -Force
                $migratedCount++
            }
        }
        
        if ($migratedCount -gt 0) {
            Write-Host "   Migrated $migratedCount important items to cold store" -ForegroundColor Green
        }
    }
    
    # Check hot RAM size and move older items to warm store
    if (Test-Path $hotRamPath) {
        $hotRamItems = Get-ChildItem $hotRamPath -Filter "*.json"
        if ($hotRamItems.Count -gt 30) {  # Arbitrary limit
            $movedCount = 0
            $hotRamItems | Sort-Object LastWriteTime | Select-Object -First ($hotRamItems.Count - 20) | ForEach-Object {
                $item = Get-Content $_.FullName | ConvertFrom-Json
                $ageHours = ((Get-Date) - [DateTime]::Parse($item.timestamp)).TotalHours
                
                if ($ageHours -gt 2) {  # Older than 2 hours
                    Copy-Item $_.FullName (Join-Path $warmStorePath $_.Name)
                    Remove-Item $_.FullName -Force
                    $movedCount++
                }
            }
            
            if ($movedCount -gt 0) {
                Write-Host "   Moved $movedCount older items from hot RAM to warm store" -ForegroundColor Green
            }
        }
    }
}

function Learn-UsagePatterns {
    param([hashtable]$Metrics)
    
    Write-Host "📚 Learning usage patterns..." -ForegroundColor Yellow
    
    # Analyze popular topics from memory content
    $allItems = @()
    
    foreach ($path in @("memory-system/hot-ram", "memory-system/warm-store", "memory-system/cold-store/content")) {
        if (Test-Path $path) {
            $allItems += Get-ChildItem $path -Filter "*.json" -ErrorAction SilentlyContinue
        }
    }
    
    # Extract topics from metadata
    $topicFrequency = @{}
    foreach ($itemFile in $allItems) {
        $item = Get-Content $itemFile.FullName | ConvertFrom-Json
        if ($item.metadata -and $item.metadata.tags) {
            foreach ($tag in $item.metadata.tags) {
                if ($topicFrequency.ContainsKey($tag)) {
                    $topicFrequency[$tag]++
                } else {
                    $topicFrequency[$tag] = 1
                }
            }
        }
    }
    
    # Update usage patterns
    if (Test-Path $usagePatternsPath) {
        $usagePatterns = Get-Content $usagePatternsPath | ConvertFrom-Json
    } else {
        $usagePatterns = @{
            totalQueries = 0
            successfulRetrievals = 0
            averageSimilarity = 0
            popularTopics = @()
            accessPatterns = @{}
        }
    }
    
    # Update popular topics (top 10)
    $usagePatterns.popularTopics = $topicFrequency.GetEnumerator() | 
        Sort-Object Value -Descending | 
        Select-Object -First 10 | 
        ForEach-Object { @{ topic = $_.Key; frequency = $_.Value } }
    
    $usagePatterns | ConvertTo-Json -Depth 10 | Out-File $usagePatternsPath -Encoding UTF8
    
    Write-Host "   Learned $(($usagePatterns.popularTopics | Measure-Object).Count) topic patterns" -ForegroundColor Green
    
    # Display top topics
    if ($usagePatterns.popularTopics.Count -gt 0) {
        Write-Host "   Top topics:" -ForegroundColor Cyan
        $usagePatterns.popularTopics | Select-Object -First 5 | ForEach-Object {
            Write-Host "     - $($_.topic): $($_.frequency) occurrences" -ForegroundColor Gray
        }
    }
}

function Update-EmbeddingModel {
    Write-Host "🔤 Checking embedding model..." -ForegroundColor Yellow
    
    # Placeholder for embedding model updates
    # In production, this would:
    # 1. Check for new embedding model versions
    # 2. Test performance with sample queries
    # 3. Update if significant improvement found
    
    $currentModel = $config.storage.embeddingModel
    Write-Host "   Current model: $currentModel" -ForegroundColor Gray
    Write-Host "   (Embedding model updates require manual implementation)" -ForegroundColor Gray
}

function Generate-EvolutionReport {
    param(
        [hashtable]$Metrics,
        [hashtable]$Analysis,
        [hashtable]$Changes
    )
    
    Write-Host "📋 Generating evolution report..." -ForegroundColor Yellow
    
    $report = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        evolutionCycle = if ($metrics.evolution) { $metrics.evolution.totalCycles + 1 } else { 1 }
        performanceAnalysis = $analysis
        changesMade = $changes
        recommendations = $analysis.recommendations
        nextEvolution = (Get-Date).AddDays($config.evolution.modelUpdateIntervalDays).ToString("yyyy-MM-dd")
    }
    
    $reportPath = "memory-system/system-state/evolution-report-$(Get-Date -Format 'yyyy-MM-dd').json"
    $report | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8
    
    # Update evolution metrics
    if (Test-Path $evolutionMetricsPath) {
        $evolutionMetrics = Get-Content $evolutionMetricsPath | ConvertFrom-Json
    } else {
        $evolutionMetrics = @{
            totalCycles = 0
            lastEvolution = $null
            performanceImprovements = @()
            modelUpdates = 0
        }
    }
    
    $evolutionMetrics.totalCycles++
    $evolutionMetrics.lastEvolution = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    
    # Record performance improvement if any
    if ($analysis.retrievalEffectiveness -gt 0) {
        $evolutionMetrics.performanceImprovements += @{
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            retrievalEffectiveness = $analysis.retrievalEffectiveness
            pruningEfficiency = $analysis.pruningEfficiency
            storageOptimization = $analysis.storageOptimization
        }
        
        # Keep only last 10 improvements
        if ($evolutionMetrics.performanceImprovements.Count -gt 10) {
            $evolutionMetrics.performanceImprovements = $evolutionMetrics.performanceImprovements | Select-Object -Last 10
        }
    }
    
    $evolutionMetrics | ConvertTo-Json -Depth 10 | Out-File $evolutionMetricsPath -Encoding UTF8
    
    Write-Host "   Report saved: $reportPath" -ForegroundColor Green
    
    # Display summary
    Write-Host ""
    Write-Host "📊 Evolution Summary" -ForegroundColor Cyan
    Write-Host "   Cycle: $($report.evolutionCycle)" -ForegroundColor White
    Write-Host "   Retrieval Effectiveness: $($analysis.retrievalEffectiveness.ToString('P1'))" -ForegroundColor White
    Write-Host "   Pruning Efficiency: $($analysis.pruningEfficiency.ToString('P1'))" -ForegroundColor White
    Write-Host "   Storage Optimization: $($analysis.storageOptimization.ToString('P1'))" -ForegroundColor White
    Write-Host "   Changes Made: $(if ($changes.Count -gt 0) { $changes.Count } else { 'None' })" -ForegroundColor White
    Write-Host "   Next Evolution: $($report.nextEvolution)" -ForegroundColor White
}

# Main evolution routine
Write-Host "🕐 Starting evolution cycle at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Load current metrics
$metrics = Load-Metrics
Write-Host "📈 Loaded system metrics" -ForegroundColor Green
Write-Host ""

# Track changes made during this evolution cycle
$changesMade = @{}

# 1. Analyze current performance
$analysis = Analyze-Performance -Metrics $metrics
Write-Host ""

# 2. Optimize pruning thresholds
Optimize-PruningThresholds -Metrics $metrics -Analysis $analysis
Write-Host ""

# 3. Optimize storage tiers
Optimize-StorageTiers -Analysis $analysis
Write-Host ""

# 4. Learn from usage patterns
Learn-UsagePatterns -Metrics $metrics
Write-Host ""

# 5. Check for embedding model updates
Update-EmbeddingModel
Write-Host ""

# 6. Generate evolution report
Generate-EvolutionReport -Metrics $metrics -Analysis $analysis -Changes $changesMade
Write-Host ""

Write-Host "✅ Evolution cycle completed successfully" -ForegroundColor Green
Write-Host "🔄 Next evolution scheduled for $(Get-Date).AddDays($($config.evolution.modelUpdateIntervalDays)).ToString('yyyy-MM-dd')" -ForegroundColor Cyan

# Log completion
$logEntry = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    action = "evolution-cycle"
    status = "completed"
    analysis = $analysis
} | ConvertTo-Json -Compress

$logFile = "memory-system/system-state/evolution-log.jsonl"
$logEntry | Out-File $logFile -Append -Encoding UTF8