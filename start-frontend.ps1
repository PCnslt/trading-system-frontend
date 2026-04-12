# PowerShell script to start the Trading System Frontend
Write-Host "Starting Trading System Frontend..." -ForegroundColor Green

# Change to frontend directory
Set-Location "C:\Users\pcnsl\.openclaw\workspace\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies. Please check npm configuration." -ForegroundColor Red
        exit 1
    }
}

# Check Angular CLI
try {
    $ngVersion = npx ng version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Angular CLI is available" -ForegroundColor Green
        
        # Clear previous logs
        if (Test-Path "angular-errors.log") { Remove-Item "angular-errors.log" }
        if (Test-Path "angular-output.log") { Remove-Item "angular-output.log" }
        if (Test-Path "frontend-error.log") { Remove-Item "frontend-error.log" }
        if (Test-Path "frontend.log") { Remove-Item "frontend.log" }
        
        # Build the project first to check for errors
        Write-Host "Building frontend..." -ForegroundColor Cyan
        npx ng build --configuration development
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build successful! Starting development server..." -ForegroundColor Green
            Write-Host "Frontend will be available at: http://localhost:4200" -ForegroundColor Green
            Write-Host "API URL: http://localhost:8082/api" -ForegroundColor Green
            Write-Host "WebSocket URL: http://localhost:8082/ws-monitoring" -ForegroundColor Green
            
            # Start the development server
            npx ng serve --open --port 4200
        } else {
            Write-Host "Build failed. Please fix the errors above." -ForegroundColor Red
        }
    } else {
        Write-Host "Angular CLI not found. Installing..." -ForegroundColor Yellow
        npm install -g @angular/cli
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Angular CLI installed. Please run this script again." -ForegroundColor Green
        } else {
            Write-Host "Failed to install Angular CLI." -ForegroundColor Red
        }
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Trying alternative startup method..." -ForegroundColor Yellow
    
    # Try using npm start
    Write-Host "Using npm start..." -ForegroundColor Cyan
    npm start
}