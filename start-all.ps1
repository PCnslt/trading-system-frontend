# PowerShell script to start the entire Trading System
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   TRADING SYSTEM STARTUP SCRIPT" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting all components of the Trading System..." -ForegroundColor Green
Write-Host "`nComponents:" -ForegroundColor White
Write-Host "1. Backend API (Spring Boot) - Port 8082" -ForegroundColor Yellow
Write-Host "2. Frontend Dashboard (Angular) - Port 4200" -ForegroundColor Yellow
Write-Host "3. Trading Agents (Python)" -ForegroundColor Yellow
Write-Host "`nNote: Start components in separate terminals for best results." -ForegroundColor Magenta

# Function to check if a port is in use
function Test-PortInUse {
    param([int]$Port)
    $result = netstat -ano | findstr ":$Port"
    return [bool]$result
}

# Check required ports
Write-Host "`nChecking ports..." -ForegroundColor Cyan
$ports = @(8082, 4200)
foreach ($port in $ports) {
    if (Test-PortInUse -Port $port) {
        Write-Host "Port $port is already in use." -ForegroundColor Red
    } else {
        Write-Host "Port $port is available." -ForegroundColor Green
    }
}

# Display startup options
Write-Host "`nStartup Options:" -ForegroundColor Cyan
Write-Host "1. Start Backend only" -ForegroundColor White
Write-Host "2. Start Frontend only" -ForegroundColor White
Write-Host "3. Start Agents only" -ForegroundColor White
Write-Host "4. Start All (recommended in separate terminals)" -ForegroundColor White
Write-Host "5. Start with Docker Compose" -ForegroundColor White
Write-Host "6. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host "Starting Backend..." -ForegroundColor Green
        & "$PSScriptRoot\start-backend.ps1"
    }
    "2" {
        Write-Host "Starting Frontend..." -ForegroundColor Green
        & "$PSScriptRoot\start-frontend.ps1"
    }
    "3" {
        Write-Host "Starting Agents..." -ForegroundColor Green
        & "$PSScriptRoot\start-agents.ps1"
    }
    "4" {
        Write-Host "Starting all components..." -ForegroundColor Green
        Write-Host "`nOpening separate terminals for each component..." -ForegroundColor Yellow
        
        # Start backend in new terminal
        Write-Host "Starting Backend in new window..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$PSScriptRoot\start-backend.ps1`""
        
        # Wait a bit for backend to start
        Start-Sleep -Seconds 5
        
        # Start frontend in new terminal
        Write-Host "Starting Frontend in new window..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$PSScriptRoot\start-frontend.ps1`""
        
        # Wait a bit for frontend to start
        Start-Sleep -Seconds 5
        
        # Start agents in new terminal
        Write-Host "Starting Agents in new window..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$PSScriptRoot\start-agents.ps1`""
        
        Write-Host "`nAll components started in separate terminals." -ForegroundColor Green
        Write-Host "Backend: http://localhost:8082" -ForegroundColor Yellow
        Write-Host "Frontend: http://localhost:4200" -ForegroundColor Yellow
        Write-Host "H2 Console: http://localhost:8082/h2-console" -ForegroundColor Yellow
    }
    "5" {
        Write-Host "Starting with Docker Compose..." -ForegroundColor Green
        Set-Location "$PSScriptRoot\infrastructure"
        
        if (Test-Path "docker-compose.yml") {
            Write-Host "Found docker-compose.yml" -ForegroundColor Green
            docker-compose up -d
            Write-Host "Services started in Docker." -ForegroundColor Green
            Write-Host "Backend: http://localhost:8082" -ForegroundColor Yellow
            Write-Host "Frontend: http://localhost:4200" -ForegroundColor Yellow
        } else {
            Write-Host "docker-compose.yml not found." -ForegroundColor Red
        }
    }
    "6" {
        Write-Host "Exiting..." -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    }
}

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Access the application at: http://localhost:4200" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8082/api" -ForegroundColor Cyan
Write-Host "`nFor issues, check the log files in each component directory." -ForegroundColor Yellow