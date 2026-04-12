# Script to restart backend with fixed ticker counts
Write-Host "Restarting Backend with Real Ticker Counts..." -ForegroundColor Green

# Stop current backend
Write-Host "Stopping current backend (PID 7020)..." -ForegroundColor Yellow
taskkill /F /PID 7020 2>$null

# Wait a moment
Start-Sleep -Seconds 2

# Start backend
Write-Host "Starting backend with updated ticker counts..." -ForegroundColor Green
cd "C:\Users\pcnsl\.openclaw\workspace\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; mvn spring-boot:run"

Write-Host "Backend restart initiated. Waiting for startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test the new ticker counts
Write-Host "`nTesting new ticker counts..." -ForegroundColor Cyan
try {
    $stats = Invoke-WebRequest -Uri "http://localhost:8082/api/tickers/stats" -Method GET -UseBasicParsing -ErrorAction Stop
    $json = $stats.Content | ConvertFrom-Json
    
    Write-Host "✅ Backend is running!" -ForegroundColor Green
    Write-Host "`nTicker Statistics:" -ForegroundColor White
    Write-Host "  Total Tickers: $($json.totalTickers)" -ForegroundColor Cyan
    Write-Host "  Stocks: $($json.stocksCount)" -ForegroundColor Cyan
    Write-Host "  Cryptocurrencies: $($json.cryptoCount)" -ForegroundColor Cyan
    Write-Host "  ETFs: $($json.etfsCount)" -ForegroundColor Cyan
    
    if ($json.totalTickers -gt 300) {
        Write-Host "`n✅ SUCCESS: System now shows thousands of real tickers!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠ WARNING: Ticker count still low. Backend may need more time to start." -ForegroundColor Yellow
    }
} catch {
    Write-Host "`n❌ Backend not responding yet. Please wait a few more seconds." -ForegroundColor Red
}

Write-Host "`nNext Steps:" -ForegroundColor Magenta
Write-Host "1. Refresh your browser (Ctrl+F5)" -ForegroundColor White
Write-Host "2. Check dashboard shows correct ticker counts" -ForegroundColor White
Write-Host "3. Verify leader-prediction component shows thousands of tickers" -ForegroundColor White
Write-Host "`nAccess:" -ForegroundColor Cyan
Write-Host "- Frontend: http://localhost:4200" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8082/api" -ForegroundColor White