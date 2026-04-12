# Script to check all frontend data sources
Write-Host "Checking Frontend Data Sources..." -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check backend status
Write-Host "`n1. Backend API Status:" -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8082/actuator/health" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Backend health: $($health.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend not responding: $_" -ForegroundColor Red
}

# Check ticker stats
Write-Host "`n2. Ticker Statistics:" -ForegroundColor Yellow
try {
    $stats = Invoke-WebRequest -Uri "http://localhost:8082/api/tickers/stats" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $stats.Content | ConvertFrom-Json
    Write-Host "   ✅ Ticker stats loaded" -ForegroundColor Green
    Write-Host "   - Total Tickers: $($json.totalTickers)" -ForegroundColor White
    Write-Host "   - Stocks: $($json.stocksCount)" -ForegroundColor White
    Write-Host "   - Crypto: $($json.cryptoCount)" -ForegroundColor White
    Write-Host "   - ETFs: $($json.etfsCount)" -ForegroundColor White
    
    if ($json.totalTickers -lt 300) {
        Write-Host "   ⚠️  WARNING: Ticker count low ($($json.totalTickers)). Should be ~350." -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Failed to load ticker stats: $_" -ForegroundColor Red
}

# Check recommendations
Write-Host "`n3. Trade Recommendations:" -ForegroundColor Yellow
try {
    $recs = Invoke-WebRequest -Uri "http://localhost:8082/api/recommendations" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $recs.Content | ConvertFrom-Json
    Write-Host "   ✅ Recommendations loaded: $($json.length) items" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to load recommendations: $_" -ForegroundColor Red
}

# Check agent status
Write-Host "`n4. Agent Status:" -ForegroundColor Yellow
try {
    $agents = Invoke-WebRequest -Uri "http://localhost:8082/api/agents/status" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $agents.Content | ConvertFrom-Json
    Write-Host "   ✅ Agent status loaded: $($json.length) agents" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to load agent status: $_" -ForegroundColor Red
}

# Check chat messages
Write-Host "`n5. Chat Messages:" -ForegroundColor Yellow
try {
    $chat = Invoke-WebRequest -Uri "http://localhost:8082/api/chat/recent" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $chat.Content | ConvertFrom-Json
    Write-Host "   ✅ Chat messages loaded: $($json.length) messages" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to load chat messages: $_" -ForegroundColor Red
}

# Check frontend status
Write-Host "`n6. Frontend Status:" -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:4200" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ Frontend is running: $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend not responding: $_" -ForegroundColor Red
}

Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Magenta
Write-Host "- Refresh browser (Ctrl+F5) to see UI fixes" -ForegroundColor White
Write-Host "- Check dashboard for readable text" -ForegroundColor White
Write-Host "- Verify ticker counts show ~350 (not 67)" -ForegroundColor White
Write-Host "- Test all dashboard components" -ForegroundColor White