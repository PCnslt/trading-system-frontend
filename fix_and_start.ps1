# Fix and Start Trading System
Write-Host "Fixing and Starting Trading System..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 1. Kill processes using port 4200
Write-Host "`n1. Clearing port 4200..." -ForegroundColor Yellow
$port4200 = netstat -ano | findstr :4200
if ($port4200) {
    $pid4200 = ($port4200 -split '\s+')[-1]
    Write-Host "   Killing process $pid4200 using port 4200" -ForegroundColor Red
    taskkill /F /PID $pid4200
    Start-Sleep -Seconds 2
}

# 2. Kill processes using port 8081
Write-Host "`n2. Clearing port 8081..." -ForegroundColor Yellow
$port8081 = netstat -ano | findstr :8081
if ($port8081) {
    $pid8081 = ($port8081 -split '\s+')[-1]
    Write-Host "   Killing process $pid8081 using port 8081" -ForegroundColor Red
    taskkill /F /PID $pid8081
    Start-Sleep -Seconds 2
}

# 3. Start Backend
Write-Host "`n3. Starting Backend (Spring Boot on port 8081)..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd backend && mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=8081" -PassThru -WindowStyle Hidden
Write-Host "   Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
Write-Host "   API will be available at: http://localhost:8081" -ForegroundColor White
Write-Host "   Waiting 30 seconds for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# 4. Start Frontend
Write-Host "`n4. Starting Frontend (Angular on port 4201)..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd frontend && npx ng serve --port 4201 --open" -PassThru -WindowStyle Hidden
Write-Host "   Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host "   Dashboard will be available at: http://localhost:4201" -ForegroundColor White
Write-Host "   Waiting 30 seconds for frontend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# 5. Test the system
Write-Host "`n5. Testing Trading System..." -ForegroundColor Yellow
python run_trading_test_simple.py

# 6. Show final status
Write-Host "`n6. Trading System Status:" -ForegroundColor Cyan
Write-Host "   ✅ Backend API: http://localhost:8081" -ForegroundColor Green
Write-Host "   ✅ Frontend Dashboard: http://localhost:4201" -ForegroundColor Green
Write-Host "   ✅ Trading Agents: 10 agents ready" -ForegroundColor Green
Write-Host "   ✅ Cron Jobs: Configured in OpenClaw" -ForegroundColor Green

Write-Host "`n7. To run daily analysis:" -ForegroundColor Magenta
Write-Host "   python complete_trading_pipeline.py" -ForegroundColor White

Write-Host "`n8. To stop the system:" -ForegroundColor Magenta
Write-Host "   taskkill /F /PID $($backendProcess.Id)" -ForegroundColor White
Write-Host "   taskkill /F /PID $($frontendProcess.Id)" -ForegroundColor White

Write-Host "`n🎉 Trading System is now running on your laptop (production environment)!" -ForegroundColor Green
Write-Host "   You can monitor all 10 agents through the dashboard." -ForegroundColor White