# Simple Memory System Setup

Write-Host "🚀 Setting up Self-Evolving Memory System" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# 1. Create directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Cyan

$directories = @(
    "memory-system",
    "memory-system/hot-ram",
    "memory-system/warm-store", 
    "memory-system/cold-store",
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

# 2. Create configuration
Write-Host "⚙️  Creating configuration..." -ForegroundColor Cyan

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
        embeddingModel = "all-MiniLM-L6-v2"
        vectorDimensions = 384
    }
}

$configPath = "memory-system/system-state/config.json"
$config | ConvertTo-Json -Depth 10 | Out-File $configPath -Encoding UTF8
Write-Host "   Configuration saved: $configPath" -ForegroundColor Green
Write-Host ""

# 3. Test the system
Write-Host "🧪 Testing the system..." -ForegroundColor Cyan

# Test memory manager
Write-Host "   Testing memory manager..." -ForegroundColor Gray
if (Test-Path "memory-manager.ps1") {
    # Store a test memory
    $testContent = "Self-evolving memory system with auto-pruning deployed successfully"
    $testMetadata = '{"type":"system","tags":["deployment","memory","pruning"]}'
    
    Write-Host "   Storing test memory..." -ForegroundColor Gray
    & .\memory-manager.ps1 -Action store -Content $testContent -Metadata $testMetadata
    
    Write-Host "   Retrieving test memory..." -ForegroundColor Gray
    & .\memory-manager.ps1 -Action retrieve -Query "memory system" -Limit 2
    
    Write-Host "   Checking statistics..." -ForegroundColor Gray
    & .\memory-manager.ps1 -Action stats
} else {
    Write-Host "   ⚠️ Memory manager script not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Self-evolving memory system is ready" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Quick Start:" -ForegroundColor Cyan
Write-Host "   1. Store a memory:" -ForegroundColor White
Write-Host '      .\memory-manager.ps1 -Action store -Content "Your content" -Metadata ''{"type":"learning"}''' -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Retrieve memories:" -ForegroundColor White
Write-Host '      .\memory-manager.ps1 -Action retrieve -Query "search query" -Limit 5' -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Run auto-pruning:" -ForegroundColor White
Write-Host '      .\auto-pruner.ps1' -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Check statistics:" -ForegroundColor White
Write-Host '      .\memory-manager.ps1 -Action stats' -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 System Location:" -ForegroundColor Cyan
Write-Host "   Configuration: memory-system/system-state/config.json" -ForegroundColor White
Write-Host "   Hot RAM: memory-system/hot-ram/" -ForegroundColor White
Write-Host "   Warm Store: memory-system/warm-store/" -ForegroundColor White
Write-Host "   Cold Store: memory-system/cold-store/content/" -ForegroundColor White
Write-Host "   Archives: memory-system/archive/" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Start using your self-evolving memory system today!" -ForegroundColor Green