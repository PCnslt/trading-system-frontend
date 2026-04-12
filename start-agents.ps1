# PowerShell script to start the Trading Agents
Write-Host "Starting Trading Agents..." -ForegroundColor Green

# Change to trading agents directory
Set-Location "C:\Users\pcnsl\.openclaw\workspace\infrastructure\trading-agents"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    Write-Host "Please edit .env file with your API keys" -ForegroundColor Yellow
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
        
        # Check if virtual environment exists
        if (Test-Path "venv") {
            Write-Host "Activating virtual environment..." -ForegroundColor Cyan
            & "venv\Scripts\Activate.ps1"
        } else {
            Write-Host "Creating virtual environment..." -ForegroundColor Yellow
            python -m venv venv
            & "venv\Scripts\Activate.ps1"
        }
        
        # Install requirements
        Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
        pip install -r requirements.txt
        
        # Check if backend is running
        Write-Host "Checking if backend is available..." -ForegroundColor Cyan
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8082/api/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "Backend is running!" -ForegroundColor Green
            }
        } catch {
            Write-Host "Backend is not running. Please start the backend first." -ForegroundColor Yellow
            Write-Host "Agents will still run but won't be able to send data to backend." -ForegroundColor Yellow
        }
        
        # Run a simple test agent
        Write-Host "Starting trading agents..." -ForegroundColor Green
        Write-Host "Available agents:" -ForegroundColor Cyan
        Write-Host "1. Technical Analyst" -ForegroundColor White
        Write-Host "2. Fundamental Analyst" -ForegroundColor White
        Write-Host "3. Sentiment Analyst" -ForegroundColor White
        Write-Host "4. Crypto Analyst" -ForegroundColor White
        Write-Host "5. Options Analyst" -ForegroundColor White
        Write-Host "6. Risk Analyst" -ForegroundColor White
        Write-Host "7. Quant Analyst" -ForegroundColor White
        Write-Host "8. Sector Analyst" -ForegroundColor White
        Write-Host "9. Compliance Analyst" -ForegroundColor White
        Write-Host "10. Macro Analyst" -ForegroundColor White
        
        Write-Host "`nRunning test system..." -ForegroundColor Cyan
        python test_system_simple.py
        
    } else {
        Write-Host "Python not found. Please install Python 3.11+." -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and in PATH." -ForegroundColor Yellow
}