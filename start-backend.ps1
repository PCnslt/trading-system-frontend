# PowerShell script to start the Trading System Backend
Write-Host "Starting Trading System Backend..." -ForegroundColor Green

# Change to backend directory
Set-Location "C:\Users\pcnsl\.openclaw\workspace\backend"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    Write-Host "Please edit .env file with your configuration" -ForegroundColor Yellow
}

# Set environment variable to use simple profile
$env:SPRING_PROFILES_ACTIVE = "simple"

# Check if Maven is available
try {
    $mvnVersion = mvn --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Maven found: $($mvnVersion | Select-Object -First 1)" -ForegroundColor Green
        
        # Clean and build the project
        Write-Host "Building backend with Maven..." -ForegroundColor Cyan
        mvn clean compile
        
        # Run the application with simple profile
        Write-Host "Starting Spring Boot application..." -ForegroundColor Cyan
        Write-Host "Backend will be available at: http://localhost:8082" -ForegroundColor Green
        Write-Host "H2 Console: http://localhost:8082/h2-console" -ForegroundColor Green
        Write-Host "Database URL: jdbc:h2:mem:tradingdb" -ForegroundColor Green
        Write-Host "Username: sa, Password: (empty)" -ForegroundColor Green
        
        mvn spring-boot:run -Dspring-boot.run.profiles=simple
    } else {
        Write-Host "Maven not found. Please install Maven or use existing JAR." -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Trying to run existing JAR file..." -ForegroundColor Yellow
    
    # Check for existing JAR file
    $jarFile = Get-ChildItem "target\*.jar" | Select-Object -First 1
    if ($jarFile) {
        Write-Host "Found JAR: $($jarFile.Name)" -ForegroundColor Green
        java -jar $jarFile.FullName --spring.profiles.active=simple
    } else {
        Write-Host "No JAR file found. Please build the project first." -ForegroundColor Red
    }
}