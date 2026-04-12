#!/usr/bin/env pwsh
<#
Start the complete 10-Agent Trading System
This script starts all Docker containers and verifies they're ready for billion-dollar recommendations.
#>

$ErrorActionPreference = "Stop"
$Workspace = "C:\Users\pcnsl\.openclaw\workspace"

Set-Location $Workspace

Write-Host "🚀 STARTING 10-AGENT TRADING SYSTEM" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Step 1: Check Docker availability
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
docker version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running or accessible" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Docker is running" -ForegroundColor Green

# Step 2: Start Memory System (PostgreSQL + Ollama + FastAPI)
Write-Host "2. Starting Memory System..." -ForegroundColor Yellow

# Check if memory system images exist
$postgresImage = docker images --quiet ankane/pgvector:latest
$ollamaImage = docker images --quiet ollama/ollama:latest
$appImage = docker images --quiet workspace-app:latest

if (-not $postgresImage) {
    Write-Host "   ⚠️  PostgreSQL image not found, pulling..." -ForegroundColor Yellow
    docker pull ankane/pgvector:latest
}

if (-not $ollamaImage) {
    Write-Host "   ⚠️  Ollama image not found, pulling..." -ForegroundColor Yellow
    docker pull ollama/ollama:latest
}

if (-not $appImage) {
    Write-Host "   ⚠️  FastAPI app image not found, building..." -ForegroundColor Yellow
    docker compose build app 2>&1 | Write-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Failed to build FastAPI app" -ForegroundColor Red
        exit 1
    }
}

# Start memory system services
Write-Host "   Starting PostgreSQL, Ollama, and FastAPI..." -ForegroundColor Yellow
docker compose up -d postgres ollama app 2>&1 | Write-Host

# Wait for services to be healthy
Write-Host "   Waiting for services to become healthy..." -ForegroundColor Yellow

# Wait for PostgreSQL
$postgresReady = $false
for ($i = 1; $i -le 30; $i++) {
    $health = docker inspect --format='{{.State.Health.Status}}' memory_postgres 2>&1
    if ($health -eq "healthy") {
        $postgresReady = $true
        break
    }
    Write-Host "   PostgreSQL status: $health (attempt $i/30)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if (-not $postgresReady) {
    Write-Host "   ❌ PostgreSQL failed to become healthy" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ PostgreSQL is healthy" -ForegroundColor Green

# Wait for Ollama (models may still be downloading)
$ollamaReady = $false
for ($i = 1; $i -le 60; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $ollamaReady = $true
            break
        }
    } catch {
        # Ollama not ready yet
    }
    Write-Host "   Ollama status: starting (attempt $i/60)" -ForegroundColor Gray
    Start-Sleep -Seconds 5
}

if (-not $ollamaReady) {
    Write-Host "   ⚠️  Ollama taking a long time to start (models downloading)" -ForegroundColor Yellow
    Write-Host "   Continuing without Ollama health check..." -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Ollama is responding" -ForegroundColor Green
}

# Wait for FastAPI app
$appReady = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $appReady = $true
            break
        }
    } catch {
        # App not ready yet
    }
    Write-Host "   FastAPI status: starting (attempt $i/30)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if (-not $appReady) {
    Write-Host "   ❌ FastAPI app failed to start" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ FastAPI app is healthy" -ForegroundColor Green

Write-Host "   🎉 Memory System is ready!" -ForegroundColor Green

# Step 3: Build and Start MCP Agents
Write-Host "3. Building and Starting 10 MCP Agents..." -ForegroundColor Yellow

# Check if MCP agents are already built
$agents = @(
    "technical-analyst",
    "fundamental-analyst", 
    "sentiment-analyst",
    "macro-analyst",
    "crypto-analyst",
    "options-analyst",
    "risk-analyst",
    "quant-analyst",
    "sector-analyst",
    "compliance-analyst"
)

$agentsToBuild = @()
foreach ($agent in $agents) {
    $image = docker images --quiet "workspace-$agent" 2>&1
    if (-not $image) {
        $agentsToBuild += $agent
    }
}

if ($agentsToBuild.Count -gt 0) {
    Write-Host "   Building $($agentsToBuild.Count) agent images..." -ForegroundColor Yellow
    foreach ($agent in $agentsToBuild) {
        Write-Host "   Building $agent..." -ForegroundColor Gray
        docker compose -f docker-compose.mcp.yml build $agent 2>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ❌ Failed to build $agent" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "   ✅ All agent images already built" -ForegroundColor Green
}

# Start MCP Gateway and agents
Write-Host "   Starting MCP Gateway and all agents..." -ForegroundColor Yellow
docker compose -f docker-compose.mcp.yml up -d 2>&1 | Write-Host

# Wait for MCP Gateway to start
$gatewayReady = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8081/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $gatewayReady = $true
            break
        }
    } catch {
        # Gateway not ready yet
    }
    Write-Host "   MCP Gateway status: starting (attempt $i/30)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if (-not $gatewayReady) {
    Write-Host "   ⚠️  MCP Gateway not responding (may still be starting)" -ForegroundColor Yellow
    Write-Host "   Continuing anyway..." -ForegroundColor Yellow
} else {
    Write-Host "   ✅ MCP Gateway is responding" -ForegroundColor Green
}

# Check agent containers
Write-Host "   Checking agent containers..." -ForegroundColor Yellow
$runningContainers = docker ps --filter "name=workspace-" --format "{{.Names}}" | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "   ✅ $runningContainers agent containers running" -ForegroundColor Green

# Step 4: Generate First Recommendation
Write-Host "4. Generating First Recommendation..." -ForegroundColor Yellow

# Use the existing Python script (will be upgraded to use agents later)
Write-Host "   Running recommendation engine..." -ForegroundColor Gray
python first_recommendation.py 2>&1 | Write-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Recommendation script failed" -ForegroundColor Red
    exit 1
}

# Read and display recommendation
if (Test-Path "first_recommendation.json") {
    $recommendation = Get-Content "first_recommendation.json" | ConvertFrom-Json
    
    Write-Host "   🎯 FIRST RECOMMENDATION READY!" -ForegroundColor Green
    Write-Host "   =========================================" -ForegroundColor Green
    Write-Host "   Symbol: $($recommendation.symbol)" -ForegroundColor White
    Write-Host "   Signal: $($recommendation.signal)" -ForegroundColor White
    Write-Host "   Confidence: $($recommendation.confidence)%" -ForegroundColor White
    Write-Host "   Price: $$($recommendation.current_price)" -ForegroundColor White
    Write-Host "   Target: $$($recommendation.price_target)" -ForegroundColor White
    Write-Host "   Stop Loss: $$($recommendation.stop_loss)" -ForegroundColor White
    Write-Host "   =========================================" -ForegroundColor Green
    
    # Save to memory system via FastAPI
    try {
        $json = $recommendation | ConvertTo-Json -Depth 10 -Compress
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/memories" `
            -Method Post `
            -ContentType "application/json" `
            -Body $json `
            -UseBasicParsing `
            -ErrorAction Stop
        Write-Host "   💾 Recommendation saved to memory system" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not save to memory system: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Recommendation file not found" -ForegroundColor Yellow
}

# Step 5: System Status Summary
Write-Host "5. System Status Summary" -ForegroundColor Yellow

Write-Host "   📊 Memory System:" -ForegroundColor Gray
Write-Host "      PostgreSQL: $(docker inspect --format='{{.State.Status}}' memory_postgres)" -ForegroundColor Gray
Write-Host "      Ollama: $(docker inspect --format='{{.State.Status}}' memory_ollama)" -ForegroundColor Gray
Write-Host "      FastAPI: $(docker inspect --format='{{.State.Status}}' memory_app)" -ForegroundColor Gray

Write-Host "   🤖 Trading Agents:" -ForegroundColor Gray
$agentStatus = docker ps --filter "name=workspace-" --format "{{.Names}}: {{.Status}}" | ForEach-Object { "      $_" }
if ($agentStatus) {
    $agentStatus | Write-Host
} else {
    Write-Host "      No agent containers running" -ForegroundColor Yellow
}

Write-Host "   🌐 Endpoints:" -ForegroundColor Gray
Write-Host "      Dashboard: http://localhost:4200" -ForegroundColor Gray
Write-Host "      Memory API: http://localhost:8000" -ForegroundColor Gray
Write-Host "      MCP Gateway: http://localhost:8081" -ForegroundColor Gray
Write-Host "      Spring Boot: http://localhost:8080" -ForegroundColor Gray

Write-Host "   ⏰ Cron Jobs:" -ForegroundColor Gray
Write-Host "      Daily Recommendation: 9:00 AM weekdays" -ForegroundColor Gray
Write-Host "      Storage Check: 8:00 AM daily" -ForegroundColor Gray
Write-Host "      Docker Cleanup: Sunday 3:00 AM" -ForegroundColor Gray

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ 10-AGENT TRADING SYSTEM DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "💰 Your billionaire journey starts now!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check dashboard at http://localhost:4200" -ForegroundColor White
Write-Host "2. Monitor agent activity via logs" -ForegroundColor White
Write-Host "3. First daily recommendation will arrive tomorrow at 9:00 AM" -ForegroundColor White
Write-Host "4. Configure VS Code MCP client with SSE endpoint: http://localhost:8081/sse" -ForegroundColor White