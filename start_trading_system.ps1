# Start Trading System
Write-Host "Starting Trading System..." -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

# 1. Start Backend (Spring Boot)
Write-Host "`n1. Starting Backend (Spring Boot)..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    cd backend
    mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=8081
}

# 2. Start Frontend (Angular)
Write-Host "`n2. Starting Frontend (Angular)..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    cd frontend
    npx ng serve --port 4201 --open
}

# 3. Run Trading Agents Test
Write-Host "`n3. Testing Trading Agents..." -ForegroundColor Yellow
python run_trading_test_simple.py

# 4. Show Status
Write-Host "`n4. System Status:" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8081" -ForegroundColor White
Write-Host "   Frontend Dashboard: http://localhost:4201" -ForegroundColor White
Write-Host "   Trading Agents: Ready (10 agents)" -ForegroundColor White
Write-Host "   Cron Jobs: Daily analysis at 9 AM, Progress checks at 9,12,15,18,21" -ForegroundColor White

# 5. Keep running
Write-Host "`n5. System is running. Press Ctrl+C to stop." -ForegroundColor Magenta
Write-Host "`nTo run daily analysis manually:" -ForegroundColor Gray
Write-Host "   python complete_trading_pipeline.py" -ForegroundColor Gray

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`nStopping Trading System..." -ForegroundColor Red
    Stop-Job $backendJob
    Stop-Job $frontendJob
    Remove-Job $backendJob
    Remove-Job $frontendJob
}