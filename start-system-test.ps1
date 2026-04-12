# Comprehensive System Test Script
Write-Host "🚀 Starting Trading System Test..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Step 1: Check if frontend is running
Write-Host "`n1. Checking Frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:4200" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Frontend is running on port 4200" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend not running. Starting it..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npx ng serve --port 4200 --open"
    Write-Host "   ⏳ Waiting for frontend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Step 2: Check/Start Backend
Write-Host "`n2. Checking Backend..." -ForegroundColor Yellow
$backendRunning = $false
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8082/actuator/health" -Method GET -UseBasicParsing -ErrorAction Stop
    if ($health.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is running on port 8082" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host "   ❌ Backend not running. Starting it..." -ForegroundColor Yellow
}

if (-not $backendRunning) {
    # Kill any existing backend process
    Get-Process -Name "java" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*trading-system*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Start backend
    Write-Host "   ⏳ Starting backend with H2 database..." -ForegroundColor Yellow
    $backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; `$env:SPRING_PROFILES_ACTIVE='simple'; mvn spring-boot:run" -PassThru
    Write-Host "   ⏳ Waiting for backend to start (30 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Step 3: Test Backend APIs
Write-Host "`n3. Testing Backend APIs..." -ForegroundColor Yellow

# Test health endpoint
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8082/actuator/health" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Backend health: $($health.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend health check failed" -ForegroundColor Red
    exit 1
}

# Test ticker stats
try {
    $stats = Invoke-WebRequest -Uri "http://localhost:8082/api/tickers/stats" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $stats.Content | ConvertFrom-Json
    Write-Host "   ✅ Ticker stats loaded" -ForegroundColor Green
    Write-Host "   - Total Tickers: $($json.totalTickers)" -ForegroundColor White
    Write-Host "   - Stocks: $($json.stocksCount)" -ForegroundColor White
    Write-Host "   - Crypto: $($json.cryptoCount)" -ForegroundColor White
    Write-Host "   - ETFs: $($json.etfsCount)" -ForegroundColor White
    
    if ($json.totalTickers -gt 300) {
        Write-Host "   ✅ Ticker count is correct (~350 real tickers)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Ticker count low: $($json.totalTickers) (should be ~350)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Failed to load ticker stats" -ForegroundColor Red
}

# Test recommendations
try {
    $recs = Invoke-WebRequest -Uri "http://localhost:8082/api/recommendations" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $recs.Content | ConvertFrom-Json
    Write-Host "   ✅ Recommendations loaded: $($json.length) items" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to load recommendations (might be empty)" -ForegroundColor Yellow
}

# Test agent status
try {
    $agents = Invoke-WebRequest -Uri "http://localhost:8082/api/agents/status" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $agents.Content | ConvertFrom-Json
    Write-Host "   ✅ Agent status loaded: $($json.length) agents" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to load agent status" -ForegroundColor Yellow
}

# Step 4: Test Frontend-Backend Integration
Write-Host "`n4. Testing Frontend-Backend Integration..." -ForegroundColor Yellow
try {
    # Test if frontend can reach backend
    $test = Invoke-WebRequest -Uri "http://localhost:4200" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Frontend is accessible" -ForegroundColor Green
    
    # Check CORS
    Write-Host "   ⚙️  Testing CORS configuration..." -ForegroundColor White
    $corsTest = Invoke-WebRequest -Uri "http://localhost:8082/api/tickers/stats" -Method OPTIONS -UseBasicParsing -Headers @{"Origin" = "http://localhost:4200"} -ErrorAction SilentlyContinue
    if ($corsTest.Headers["Access-Control-Allow-Origin"] -eq "http://localhost:4200") {
        Write-Host "   ✅ CORS properly configured" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  CORS headers not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Frontend integration test failed" -ForegroundColor Red
}

# Step 5: Start Trading Agents (if needed)
Write-Host "`n5. Checking Trading Agents..." -ForegroundColor Yellow
try {
    # Check if agents are running
    $agentProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*trading-agent*" }
    if ($agentProcesses.Count -gt 0) {
        Write-Host "   ✅ $($agentProcesses.Count) trading agents running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  No trading agents running. Start them with:" -ForegroundColor Yellow
        Write-Host "      cd infrastructure\trading-agents" -ForegroundColor White
        Write-Host "      python main.py" -ForegroundColor White
    }
} catch {
    Write-Host "   ⚠️  Could not check agent processes" -ForegroundColor Yellow
}

# Step 6: Generate Test Data
Write-Host "`n6. Generating Test Data..." -ForegroundColor Yellow
try {
    # Generate some recommendations
    $generate = Invoke-WebRequest -Uri "http://localhost:8082/api/recommendations/generate" -Method POST -UseBasicParsing -ErrorAction SilentlyContinue
    if ($generate.StatusCode -eq 200) {
        Write-Host "   ✅ Test recommendations generated" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Could not generate recommendations" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Recommendation generation endpoint not available" -ForegroundColor Yellow
}

# Step 7: Final System Check
Write-Host "`n7. Final System Status:" -ForegroundColor Magenta
Write-Host "   - Frontend: http://localhost:4200" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8082/api" -ForegroundColor White
Write-Host "   - H2 Console: http://localhost:8082/h2-console" -ForegroundColor White
Write-Host "   - JDBC URL: jdbc:h2:mem:tradingdb" -ForegroundColor White
Write-Host "   - Username: sa" -ForegroundColor White
Write-Host "   - Password: (empty)" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Refresh browser: Ctrl+F5 at http://localhost:4200" -ForegroundColor White
Write-Host "2. Verify:" -ForegroundColor White
Write-Host "   - Dashboard shows ~350 tickers" -ForegroundColor White
Write-Host "   - All text is readable (no contrast issues)" -ForegroundColor White
Write-Host "   - Chat and leader components work" -ForegroundColor White
Write-Host "3. Generate recommendations via dashboard" -ForegroundColor White
Write-Host "4. Test chat functionality" -ForegroundColor White
Write-Host "5. Check leader predictions" -ForegroundColor White

Write-Host "`n✅ System test complete!" -ForegroundColor Green