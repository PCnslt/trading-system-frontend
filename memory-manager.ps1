# Memory Manager - Core Memory Operations
# Manages storage, retrieval, pruning, and evolution of memory system

param(
    [string]$Action = "help",
    [string]$Content,
    [string]$Metadata,
    [string]$Query,
    [int]$Limit = 10,
    [float]$Threshold = 0.3
)

# Import configuration
$configPath = "memory-system/system-state/config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
} else {
    # Default configuration
    $config = @{
        pruning = @{
            hotRamMaxTokens = 4096
            warmStoreRetentionDays = 7
            archiveRetentionDays = 90
            pruningThreshold = 0.3
            autoPruneIntervalMinutes = 15
        }
        storage = @{
            compressionLevel = 6
            embeddingModel = "all-MiniLM-L6-v2"
            vectorDimensions = 384
        }
    }
}

# Utility functions
function Get-CurrentTimestamp {
    return (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

function Calculate-Importance {
    param(
        [string]$Text,
        [hashtable]$Metadata
    )
    
    # Simple importance calculation based on content features
    $score = 0.5  # Base score
    
    # Boost for certain content types
    if ($Metadata.type -eq "learning") { $score += 0.3 }
    if ($Metadata.type -eq "decision") { $score += 0.4 }
    if ($Metadata.userFlagged -eq $true) { $score += 0.5 }
    
    # Boost for code content
    if ($Text -match "```(?:powershell|javascript|python|sql|html)") {
        $score += 0.2
    }
    
    # Boost for structured content (lists, steps)
    if ($Text -match "^\s*[\d\-•].*$" -or $Text -match "step|phase|stage") {
        $score += 0.1
    }
    
    # Cap at 1.0
    return [Math]::Min($score, 1.0)
}

function Get-Embedding {
    param([string]$Text)
    
    # Simple placeholder for embedding generation
    # In production, use Ollama, OpenAI, or local embedding model
    $words = $Text -split '\s+' | Select-Object -First 50
    $embedding = @()
    
    # Create simple bag-of-words style embedding (placeholder)
    for ($i = 0; $i -lt 384; $i++) {
        $embedding += [Math]::Sin($i * 0.1) * 0.5  # Placeholder values
    }
    
    return $embedding
}

function Calculate-Similarity {
    param(
        [array]$Embedding1,
        [array]$Embedding2
    )
    
    # Simple cosine similarity (placeholder)
    if ($Embedding1.Count -ne $Embedding2.Count) {
        return 0.0
    }
    
    $dot = 0.0
    $norm1 = 0.0
    $norm2 = 0.0
    
    for ($i = 0; $i -lt $Embedding1.Count; $i++) {
        $dot += $Embedding1[$i] * $Embedding2[$i]
        $norm1 += $Embedding1[$i] * $Embedding1[$i]
        $norm2 += $Embedding2[$i] * $Embedding2[$i]
    }
    
    if ($norm1 -eq 0 -or $norm2 -eq 0) {
        return 0.0
    }
    
    return $dot / ([Math]::Sqrt($norm1) * [Math]::Sqrt($norm2))
}

# Core memory operations
switch ($Action.ToLower()) {
    "store" {
        if (-not $Content) {
            Write-Host "❌ Error: Content parameter required for store action" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "💾 Storing memory item..." -ForegroundColor Cyan
        
        # Parse metadata if provided
        $metadataObj = @{}
        if ($Metadata) {
            try {
                $metadataObj = $Metadata | ConvertFrom-Json -AsHashtable
            } catch {
                Write-Host "⚠️  Could not parse metadata, using empty object" -ForegroundColor Yellow
            }
        }
        
        # Calculate importance
        $importance = Calculate-Importance -Text $Content -Metadata $metadataObj
        
        # Generate embedding
        $embedding = Get-Embedding -Text $Content
        
        # Create memory item
        $memoryItem = @{
            id = [guid]::NewGuid().ToString()
            content = $Content
            embedding = $embedding
            metadata = $metadataObj
            importance = $importance
            timestamp = Get-CurrentTimestamp
            accessCount = 0
        }
        
        # Determine storage tier based on importance
        $storagePath = "memory-system/warm-store"
        if ($importance -gt 0.8) {
            $storagePath = "memory-system/cold-store/content"
            Write-Host "📦 Storing in Cold Store (high importance: $importance)" -ForegroundColor Green
        } elseif ($importance -gt 0.5) {
            Write-Host "📚 Storing in Warm Store (medium importance: $importance)" -ForegroundColor Yellow
        } else {
            Write-Host "📝 Storing in Warm Store (low importance: $importance)" -ForegroundColor Gray
        }
        
        # Ensure directory exists
        if (-not (Test-Path $storagePath)) {
            New-Item -ItemType Directory -Force -Path $storagePath | Out-Null
        }
        
        # Save memory item
        $filePath = Join-Path $storagePath "$($memoryItem.id).json"
        $memoryItem | ConvertTo-Json -Depth 10 | Out-File $filePath -Encoding UTF8
        
        # Also store in hot RAM for immediate access
        $hotRamPath = "memory-system/hot-ram"
        if (-not (Test-Path $hotRamPath)) {
            New-Item -ItemType Directory -Force -Path $hotRamPath | Out-Null
        }
        Copy-Item $filePath (Join-Path $hotRamPath "$($memoryItem.id).json")
        
        Write-Host "✅ Memory stored successfully (ID: $($memoryItem.id))" -ForegroundColor Green
        Write-Host "   Importance: $importance" -ForegroundColor Cyan
        Write-Host "   Timestamp: $($memoryItem.timestamp)" -ForegroundColor Cyan
    }
    
    "retrieve" {
        if (-not $Query) {
            Write-Host "❌ Error: Query parameter required for retrieve action" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "🔍 Searching memories for: '$Query'" -ForegroundColor Cyan
        
        # Generate query embedding
        $queryEmbedding = Get-Embedding -Text $Query
        
        # Search in all storage tiers
        $results = @()
        
        # Search Hot RAM first (most recent)
        $hotRamPath = "memory-system/hot-ram"
        if (Test-Path $hotRamPath) {
            Get-ChildItem $hotRamPath -Filter "*.json" | ForEach-Object {
                $item = Get-Content $_.FullName | ConvertFrom-Json
                $similarity = Calculate-Similarity -Embedding1 $queryEmbedding -Embedding2 $item.embedding
                
                $results += [PSCustomObject]@{
                    Content = $item.content
                    Similarity = $similarity
                    Importance = $item.importance
                    Timestamp = $item.timestamp
                    Source = "Hot RAM"
                    Id = $item.id
                }
            }
        }
        
        # Search Warm Store
        $warmStorePath = "memory-system/warm-store"
        if (Test-Path $warmStorePath) {
            Get-ChildItem $warmStorePath -Filter "*.json" | ForEach-Object {
                $item = Get-Content $_.FullName | ConvertFrom-Json
                $similarity = Calculate-Similarity -Embedding1 $queryEmbedding -Embedding2 $item.embedding
                
                $results += [PSCustomObject]@{
                    Content = $item.content
                    Similarity = $similarity
                    Importance = $item.importance
                    Timestamp = $item.timestamp
                    Source = "Warm Store"
                    Id = $item.id
                }
            }
        }
        
        # Search Cold Store
        $coldStorePath = "memory-system/cold-store/content"
        if (Test-Path $coldStorePath) {
            Get-ChildItem $coldStorePath -Filter "*.json" | ForEach-Object {
                $item = Get-Content $_.FullName | ConvertFrom-Json
                $similarity = Calculate-Similarity -Embedding1 $queryEmbedding -Embedding2 $item.embedding
                
                $results += [PSCustomObject]@{
                    Content = $item.content
                    Similarity = $similarity
                    Importance = $item.importance
                    Timestamp = $item.timestamp
                    Source = "Cold Store"
                    Id = $item.id
                }
            }
        }
        
        # Sort by similarity and importance
        $sortedResults = $results | Sort-Object -Property @{
            Expression = { $_.Similarity * 0.7 + $_.Importance * 0.3 }
            Descending = $true
        } | Select-Object -First $Limit
        
        # Update access count for retrieved items
        foreach ($result in $sortedResults) {
            $filePath = "memory-system/$($result.Source.ToLower() -replace ' ', '-')/$($result.Id).json"
            if (Test-Path $filePath) {
                $item = Get-Content $filePath | ConvertFrom-Json
                $item.accessCount += 1
                $item | ConvertTo-Json -Depth 10 | Out-File $filePath -Encoding UTF8
            }
        }
        
        # Display results
        if ($sortedResults.Count -eq 0) {
            Write-Host "📭 No relevant memories found" -ForegroundColor Yellow
        } else {
            Write-Host "📚 Found $($sortedResults.Count) relevant memories:" -ForegroundColor Green
            Write-Host ""
            
            $i = 1
            foreach ($result in $sortedResults) {
                $similarityPercent = ($result.Similarity * 100).ToString("F1")
                $importancePercent = ($result.Importance * 100).ToString("F1")
                
                Write-Host "--- Result $i ---" -ForegroundColor Cyan
                Write-Host "Similarity: $similarityPercent%" -ForegroundColor Green
                Write-Host "Importance: $importancePercent%" -ForegroundColor Yellow
                Write-Host "Source: $($result.Source)" -ForegroundColor Gray
                Write-Host "Timestamp: $($result.Timestamp)" -ForegroundColor Gray
                Write-Host ""
                Write-Host $result.Content -ForegroundColor White
                Write-Host ""
                $i++
            }
        }
        
        return $sortedResults
    }
    
    "prune" {
        Write-Host "✂️  Running auto-pruning (threshold: $Threshold)..." -ForegroundColor Cyan
        
        # Prune Hot RAM based on access patterns and age
        $hotRamPath = "memory-system/hot-ram"
        if (Test-Path $hotRamPath) {
            $hotRamItems = Get-ChildItem $hotRamPath -Filter "*.json"
            $hotRamCount = $hotRamItems.Count
            
            if ($hotRamCount -gt 50) {  # Arbitrary limit for demo
                Write-Host "  Pruning Hot RAM ($hotRamCount items)..." -ForegroundColor Yellow
                
                # Sort by access count and age
                $itemsToPrune = $hotRamItems | ForEach-Object {
                    $item = Get-Content $_.FullName | ConvertFrom-Json
                    [PSCustomObject]@{
                        Path = $_.FullName
                        AccessCount = $item.accessCount
                        AgeHours = ((Get-Date) - [DateTime]::Parse($item.timestamp)).TotalHours
                        Importance = $item.importance
                    }
                } | Sort-Object AccessCount, AgeHours -Descending | Select-Object -Last ($hotRamCount - 25)
                
                foreach ($item in $itemsToPrune) {
                    Remove-Item $item.Path -Force
                    Write-Host "    Removed: $(Split-Path $item.Path -Leaf)" -ForegroundColor Gray
                }
            }
        }
        
        # Archive old Warm Store items
        $warmStorePath = "memory-system/warm-store"
        if (Test-Path $warmStorePath) {
            $cutoffDate = (Get-Date).AddDays(-$config.pruning.warmStoreRetentionDays)
            
            Get-ChildItem $warmStorePath -Filter "*.json" | ForEach-Object {
                $item = Get-Content $_.FullName | ConvertFrom-Json
                $itemDate = [DateTime]::Parse($item.timestamp)
                
                if ($itemDate -lt $cutoffDate) {
                    # Move to archive
                    $archivePath = "memory-system/archive"
                    if (-not (Test-Path $archivePath)) {
                        New-Item -ItemType Directory -Force -Path $archivePath | Out-Null
                    }
                    
                    $archiveFile = Join-Path $archivePath "$(Get-Date -Format 'yyyy-MM')-archive.jsonl"
                    $item | ConvertTo-Json -Compress | Out-File $archiveFile -Append -Encoding UTF8
                    
                    # Remove from warm store
                    Remove-Item $_.FullName -Force
                    Write-Host "    Archived: $(Split-Path $_.FullName -Leaf)" -ForegroundColor Gray
                }
            }
        }
        
        Write-Host "✅ Pruning completed" -ForegroundColor Green
    }
    
    "stats" {
        Write-Host "📊 Memory System Statistics" -ForegroundColor Cyan
        Write-Host "==========================" -ForegroundColor Cyan
        
        # Count items in each tier
        $hotRamCount = 0
        $warmStoreCount = 0
        $coldStoreCount = 0
        $archiveCount = 0
        
        if (Test-Path "memory-system/hot-ram") {
            $hotRamCount = (Get-ChildItem "memory-system/hot-ram" -Filter "*.json").Count
        }
        
        if (Test-Path "memory-system/warm-store") {
            $warmStoreCount = (Get-ChildItem "memory-system/warm-store" -Filter "*.json").Count
        }
        
        if (Test-Path "memory-system/cold-store/content") {
            $coldStoreCount = (Get-ChildItem "memory-system/cold-store/content" -Filter "*.json").Count
        }
        
        if (Test-Path "memory-system/archive") {
            $archiveFiles = Get-ChildItem "memory-system/archive" -Filter "*.jsonl"
            foreach ($file in $archiveFiles) {
                $archiveCount += (Get-Content $file.FullName | Measure-Object -Line).Lines
            }
        }
        
        $totalItems = $hotRamCount + $warmStoreCount + $coldStoreCount
        
        Write-Host "Hot RAM Items: $hotRamCount" -ForegroundColor Green
        Write-Host "Warm Store Items: $warmStoreCount" -ForegroundColor Yellow
        Write-Host "Cold Store Items: $coldStoreCount" -ForegroundColor Blue
        Write-Host "Archived Items: $archiveCount" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Total Active Items: $totalItems" -ForegroundColor Cyan
        Write-Host ""
        
        # Calculate average importance
        $allItems = @()
        if (Test-Path "memory-system/hot-ram") {
            $allItems += Get-ChildItem "memory-system/hot-ram" -Filter "*.json"
        }
        if (Test-Path "memory-system/warm-store") {
            $allItems += Get-ChildItem "memory-system/warm-store" -Filter "*.json"
        }
        if (Test-Path "memory-system/cold-store/content") {
            $allItems += Get-ChildItem "memory-system/cold-store/content" -Filter "*.json"
        }
        
        if ($allItems.Count -gt 0) {
            $totalImportance = 0
            foreach ($item in $allItems) {
                $data = Get-Content $item.FullName | ConvertFrom-Json
                $totalImportance += $data.importance
            }
            $avgImportance = ($totalImportance / $allItems.Count).ToString("P1")
            Write-Host "Average Importance: $avgImportance" -ForegroundColor Cyan
        }
    }
    
    "help" {
        Write-Host "🧠 Memory Manager - Self-Evolving Memory System" -ForegroundColor Cyan
        Write-Host "==============================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage: .\memory-manager.ps1 -Action [action] [parameters]" -ForegroundColor White
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Yellow
        Write-Host "  store    - Store a new memory item" -ForegroundColor Green
        Write-Host "    -Content [text]        : Content to store" -ForegroundColor Gray
        Write-Host "    -Metadata [json]       : Optional metadata (JSON string)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  retrieve - Search for relevant memories" -ForegroundColor Green
        Write-Host "    -Query [text]          : Search query" -ForegroundColor Gray
        Write-Host "    -Limit [number]        : Maximum results (default: 10)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  prune    - Run auto-pruning" -ForegroundColor Green
        Write-Host "    -Threshold [float]     : Pruning threshold (default: 0.3)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  stats    - Show system statistics" -ForegroundColor Green
        Write-Host ""
        Write-Host "  help     - Show this help message" -ForegroundColor Green
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\memory-manager.ps1 -Action store -Content 'Learned about memory systems' -Metadata '{\"type\":\"learning\",\"tags\":[\"memory\",\"ai\"]}'" -ForegroundColor Gray
        Write-Host "  .\memory-manager.ps1 -Action retrieve -Query 'memory system architecture' -Limit 5" -ForegroundColor Gray
        Write-Host "  .\memory-manager.ps1 -Action prune -Threshold 0.4" -ForegroundColor Gray
        Write-Host "  .\memory-manager.ps1 -Action stats" -ForegroundColor Gray
    }
    
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Write-Host "   Use 'help' action to see available options" -ForegroundColor Yellow
        exit 1
    }
}