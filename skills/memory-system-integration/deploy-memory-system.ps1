# Memory System Deployment Script
# Run this to deploy and test the local memory system

param(
    [switch]$PullModels = $true,
    [switch]$TestIntegration = $true
)

Write-Host "🚀 Deploying Local Memory System..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check Docker availability
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker not available. Please install Docker first." -ForegroundColor Red
    exit 1
}

# 2. Start Docker services
Write-Host "2. Starting Docker containers..." -ForegroundColor Yellow
$composeFile = "$PSScriptRoot\..\..\docker-compose.yml"
if (-not (Test-Path $composeFile)) {
    Write-Host "   ❌ docker-compose.yml not found at: $composeFile" -ForegroundColor Red
    exit 1
}

try {
    docker-compose -f $composeFile up -d
    Write-Host "   ✅ Containers started" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to start containers: $_" -ForegroundColor Red
    exit 1
}

# 3. Wait for services to be ready
Write-Host "3. Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 4. Check container status
Write-Host "4. Checking container status..." -ForegroundColor Yellow
$containers = docker-compose -f $composeFile ps
Write-Host "   Container status:" -ForegroundColor Gray
$containers | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }

# 5. Pull Ollama models if requested
if ($PullModels) {
    Write-Host "5. Pulling Ollama models..." -ForegroundColor Yellow
    try {
        Write-Host "   Pulling nomic-embed-text..." -ForegroundColor Gray
        docker exec memory_ollama ollama pull nomic-embed-text
        Write-Host "   ✅ nomic-embed-text pulled" -ForegroundColor Green
        
        Write-Host "   Pulling llama3.2:3b..." -ForegroundColor Gray
        docker exec memory_ollama ollama pull llama3.2:3b
        Write-Host "   ✅ llama3.2:3b pulled" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Failed to pull models: $_" -ForegroundColor Yellow
        Write-Host "   You can pull them manually later with:" -ForegroundColor Gray
        Write-Host "   docker exec memory_ollama ollama pull nomic-embed-text" -ForegroundColor Gray
        Write-Host "   docker exec memory_ollama ollama pull llama3.2:3b" -ForegroundColor Gray
    }
}

# 6. Load the memory module
Write-Host "6. Loading memory integration module..." -ForegroundColor Yellow
$modulePath = "$PSScriptRoot\memory.ps1"
if (Test-Path $modulePath) {
    try {
        . $modulePath
        Write-Host "   ✅ Memory module loaded" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to load memory module: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Memory module not found at: $modulePath" -ForegroundColor Red
}

# 7. Test the system
Write-Host "7. Testing memory system..." -ForegroundColor Yellow
if (Test-MemorySystem) {
    Write-Host "   ✅ Memory system is healthy!" -ForegroundColor Green
    
    # Get system stats
    $stats = Get-MemoryStats
    if ($stats) {
        Write-Host "   System statistics:" -ForegroundColor Gray
        Write-Host "   • Total memories: $($stats.memory_system.total_memories)" -ForegroundColor Gray
        Write-Host "   • Embedding model: $($stats.config.embedding_model)" -ForegroundColor Gray
        Write-Host "   • Generation model: $($stats.config.generation_model)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ Memory system health check failed" -ForegroundColor Red
}

# 8. Test integration if requested
if ($TestIntegration) {
    Write-Host "8. Testing integration..." -ForegroundColor Yellow
    if (Test-Integration) {
        Write-Host "   ✅ Integration tests passed!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Integration tests failed" -ForegroundColor Yellow
    }
}

# 9. Provide usage examples
Write-Host "9. Ready to use!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "• Store-Memory -Content 'Your text' -Tags @('tag1', 'tag2')" -ForegroundColor Gray
Write-Host "• Query-Memory -Query 'search term' -TopK 5" -ForegroundColor Gray
Write-Host "• Ask-WithContext -Question 'Your question' -MaxTokens 500" -ForegroundColor Gray
Write-Host "• Get-MemoryStats" -ForegroundColor Gray
Write-Host "• Test-MemorySystem" -ForegroundColor Gray
Write-Host ""
Write-Host "Quick test:" -ForegroundColor Yellow
Write-Host "  Store-Memory -Content 'Memory system deployed successfully on $(Get-Date)' -Tags @('deployment', 'success')" -ForegroundColor Gray
Write-Host ""
Write-Host "For full documentation, see: $PSScriptRoot\SKILL.md" -ForegroundColor Cyan

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Memory System Deployment Complete!" -ForegroundColor Green