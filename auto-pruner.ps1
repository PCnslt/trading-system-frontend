# Auto-Pruner - Context Pruning Service
# Runs periodic pruning based on configured intervals and algorithms

Write-Host "✂️  Starting Auto-Pruner Service" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Load configuration
$configPath = "memory-system/system-state/config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
} else {
    Write-Host "⚠️  Configuration not found, using defaults" -ForegroundColor Yellow
    $config = @{
        pruning = @{
            hotRamMaxTokens = 4096
            warmStoreRetentionDays = 7
            archiveRetentionDays = 90
            pruningThreshold = 0.3
            autoPruneIntervalMinutes = 15
        }
    }
}

function Get-CurrentContext {
    # Get current conversation context (simplified for demo)
    # In production, this would analyze recent messages
    return @{
        topics = @("memory", "system", "pruning", "evolution")
        timestamp = Get-Date
    }
}

function Calculate-PruningScore {
    param(
        [hashtable]$Item,
        [hashtable]$Context
    )
    
    # 1. Recency score (exponential decay over 24 hours)
    $itemTime = [DateTime]::Parse($Item.timestamp)
    $ageHours = ($Context.timestamp - $itemTime).TotalHours
    $recencyScore = [Math]::Exp(-$ageHours / 24)
    
    # 2. Relevance score (simplified - check for topic overlap)
    $relevanceScore = 0.0
    $itemText = $Item.content.ToLower()
    foreach ($topic in $Context.topics) {
        if ($itemText -match $topic.ToLower()) {
            $relevanceScore += 0.2
        }
    }
    $relevanceScore = [Math]::Min($relevanceScore, 1.0)
    
    # 3. Importance score (from stored importance)
    $importanceScore = $Item.importance
    
    # 4. Access pattern score (more accesses = more valuable)
    $accessScore = [Math]::Min($Item.accessCount / 10.0, 1.0)
    
    # Composite score with weights
    $compositeScore = (
        0.3 * $recencyScore +
        0.25 * $relevanceScore +
        0.25 * $importanceScore +
        0.2 * $accessScore
    )
    
    return @{
        Composite = $compositeScore
        Recency = $recencyScore
        Relevance = $relevanceScore
        Importance = $importanceScore
        Access = $accessScore
    }
}

function Prune-HotRam {
    Write-Host "  Pruning Hot RAM..." -ForegroundColor Yellow
    
    $hotRamPath = "memory-system/hot-ram"
    if (-not (Test-Path $hotRamPath)) {
        Write-Host "    No Hot RAM directory found" -ForegroundColor Gray
        return
    }
    
    $items = Get-ChildItem $hotRamPath -Filter "*.json"
    if ($items.Count -eq 0) {
        Write-Host "    No items in Hot RAM" -ForegroundColor Gray
        return
    }
    
    $context = Get-CurrentContext
    $prunedCount = 0
    $retainedCount = 0
    
    foreach ($itemFile in $items) {
        $item = Get-Content $itemFile.FullName | ConvertFrom-Json
        $scores = Calculate-PruningScore -Item $item -Context $context
        
        if ($scores.Composite -lt $config.pruning.pruningThreshold) {
            # Prune this item
            if ($item.importance -gt 0.7) {
                # Important item - move to cold store
                $coldStorePath = "memory-system/cold-store/content"
                if (-not (Test-Path $coldStorePath)) {
                    New-Item -ItemType Directory -Force -Path $coldStorePath | Out-Null
                }
                Copy-Item $itemFile.FullName (Join-Path $coldStorePath $itemFile.Name)
                Write-Host "    Moved to Cold Store: $($itemFile.Name)" -ForegroundColor Blue
            } else {
                # Less important item - move to warm store
                $warmStorePath = "memory-system/warm-store"
                if (-not (Test-Path $warmStorePath)) {
                    New-Item -ItemType Directory -Force -Path $warmStorePath | Out-Null
                }
                Copy-Item $itemFile.FullName (Join-Path $warmStorePath $itemFile.Name)
                Write-Host "    Moved to Warm Store: $($itemFile.Name)" -ForegroundColor Yellow
            }
            
            # Remove from hot RAM
            Remove-Item $itemFile.FullName -Force
            $prunedCount++
        } else {
            $retainedCount++
        }
    }
    
    Write-Host "    Pruned: $prunedCount items" -ForegroundColor Green
    Write-Host "    Retained: $retainedCount items" -ForegroundColor Cyan
}

function Archive-OldWarmStore {
    Write-Host "  Archiving old Warm Store items..." -ForegroundColor Yellow
    
    $warmStorePath = "memory-system/warm-store"
    if (-not (Test-Path $warmStorePath)) {
        Write-Host "    No Warm Store directory found" -ForegroundColor Gray
        return
    }
    
    $cutoffDate = (Get-Date).AddDays(-$config.pruning.warmStoreRetentionDays)
    $archivedCount = 0
    
    Get-ChildItem $warmStorePath -Filter "*.json" | ForEach-Object {
        $item = Get-Content $_.FullName | ConvertFrom-Json
        $itemDate = [DateTime]::Parse($item.timestamp)
        
        if ($itemDate -lt $cutoffDate) {
            # Archive the item
            $archivePath = "memory-system/archive"
            if (-not (Test-Path $archivePath)) {
                New-Item -ItemType Directory -Force -Path $archivePath | Out-Null
            }
            
            $archiveFile = Join-Path $archivePath "$(Get-Date -Format 'yyyy-MM')-archive.jsonl"
            
            # Add to archive (JSON Lines format)
            $archiveEntry = @{
                id = $item.id
                content = $item.content
                importance = $item.importance
                timestamp = $item.timestamp
                accessCount = $item.accessCount
                archivedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            }
            
            $archiveEntry | ConvertTo-Json -Compress | Out-File $archiveFile -Append -Encoding UTF8
            
            # Remove from warm store
            Remove-Item $_.FullName -Force
            $archivedCount++
            
            Write-Host "    Archived: $(Split-Path $_.FullName -Leaf)" -ForegroundColor Gray
        }
    }
    
    if ($archivedCount -gt 0) {
        Write-Host "    Archived $archivedCount old items" -ForegroundColor Green
    } else {
        Write-Host "    No items to archive" -ForegroundColor Gray
    }
}

function Cleanup-OldArchives {
    Write-Host "  Cleaning up old archives..." -ForegroundColor Yellow
    
    $archivePath = "memory-system/archive"
    if (-not (Test-Path $archivePath)) {
        Write-Host "    No archive directory found" -ForegroundColor Gray
        return
    }
    
    $cutoffDate = (Get-Date).AddDays(-$config.pruning.archiveRetentionDays)
    $cleanedCount = 0
    
    Get-ChildItem $archivePath -Filter "*.jsonl" | ForEach-Object {
        # Extract date from filename (format: yyyy-MM-archive.jsonl)
        if ($_.Name -match '(\d{4}-\d{2})') {
            $fileDate = [DateTime]::ParseExact($matches[1], "yyyy-MM", $null)
            
            if ($fileDate -lt $cutoffDate) {
                Remove-Item $_.FullName -Force
                $cleanedCount++
                Write-Host "    Removed old archive: $($_.Name)" -ForegroundColor Gray
            }
        }
    }
    
    if ($cleanedCount -gt 0) {
        Write-Host "    Cleaned $cleanedCount old archives" -ForegroundColor Green
    } else {
        Write-Host "    No old archives to clean" -ForegroundColor Gray
    }
}

function Update-PruningMetrics {
    $metricsPath = "memory-system/system-state/pruning-metrics.json"
    
    $metrics = @{
        lastRun = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        totalRuns = 1
        itemsPruned = 0
        itemsArchived = 0
        archivesCleaned = 0
    }
    
    # Load existing metrics if available
    if (Test-Path $metricsPath) {
        $existingMetrics = Get-Content $metricsPath | ConvertFrom-Json
        $metrics.totalRuns = $existingMetrics.totalRuns + 1
    }
    
    # Save updated metrics
    $metrics | ConvertTo-Json -Depth 10 | Out-File $metricsPath -Encoding UTF8
    
    Write-Host "  Updated pruning metrics" -ForegroundColor Cyan
}

# Main pruning routine
Write-Host "🕐 Starting pruning cycle at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# 1. Prune Hot RAM
Prune-HotRam
Write-Host ""

# 2. Archive old Warm Store items
Archive-OldWarmStore
Write-Host ""

# 3. Cleanup old archives
Cleanup-OldArchives
Write-Host ""

# 4. Update metrics
Update-PruningMetrics
Write-Host ""

Write-Host "✅ Auto-pruning completed successfully" -ForegroundColor Green
Write-Host "🔄 Next run in $($config.pruning.autoPruneIntervalMinutes) minutes" -ForegroundColor Cyan

# Log completion
$logEntry = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    action = "auto-prune"
    status = "completed"
} | ConvertTo-Json -Compress

$logFile = "memory-system/system-state/pruning-log.jsonl"
$logEntry | Out-File $logFile -Append -Encoding UTF8