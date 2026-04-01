# GitHub Integration - Manual Push Instructions

Since GitHub API tokens have expired or lack permissions, here are manual steps to push all code to GitHub:

## Step 1: Create GitHub Repositories Manually

Go to https://github.com/new and create these 3 repositories:

1. **trading-system-frontend** (Public)
   - Description: Angular 17 frontend for 10-Agent Trading System

2. **trading-system-backend** (Public)
   - Description: Spring Boot 3.2 backend for 10-Agent Trading System

3. **trading-system-infrastructure** (Public)
   - Description: Docker infrastructure for 10-Agent Trading System

## Step 2: Run the Push Script

After creating repositories, run this PowerShell script:

```powershell
# Save this as push_to_github.ps1 and run it

Write-Host "Pushing Trading System to GitHub" -ForegroundColor Green
Write-Host "=========================================="

# Replace these URLs with your actual GitHub repository URLs
$frontend_url = "https://github.com/YOUR_USERNAME/trading-system-frontend.git"
$backend_url = "https://github.com/YOUR_USERNAME/trading-system-backend.git"
$infrastructure_url = "https://github.com/YOUR_USERNAME/trading-system-infrastructure.git"

function Push-ToGitHub {
    param(
        [string]$RepoName,
        [string]$RepoUrl,
        [string]$LocalPath
    )
    
    Write-Host "`nPushing $RepoName..." -ForegroundColor Cyan
    Write-Host "Local: $LocalPath"
    Write-Host "Remote: $RepoUrl"
    
    if (Test-Path $LocalPath) {
        Set-Location $LocalPath
        
        # Initialize git if not already
        if (-not (Test-Path ".git")) {
            git init
            git add .
            git commit -m "Initial commit: $RepoName - Complete 10-Agent Trading System with real trading algorithms, live data feeds, and ML analytics"
            git branch -M main
        }
        
        # Add remote and push
        git remote add origin $RepoUrl
        git push -u origin main --force
        
        Write-Host "$RepoName pushed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Directory not found: $LocalPath" -ForegroundColor Red
    }
}

# Push all repositories
Push-ToGitHub -RepoName "trading-system-frontend" -RepoUrl $frontend_url -LocalPath "frontend"
Push-ToGitHub -RepoName "trading-system-backend" -RepoUrl $backend_url -LocalPath "backend"
Push-ToGitHub -RepoName "trading-system-infrastructure" -RepoUrl $infrastructure_url -LocalPath "."

Write-Host "`nAll repositories pushed to GitHub!" -ForegroundColor Green
Write-Host "=========================================="
```

## Step 3: Verify on GitHub

Check that all 3 repositories contain:
- Frontend: Angular 17 dashboard with agent control
- Backend: Spring Boot API with trading algorithms
- Infrastructure: Docker setup with MySQL, Redis

## Alternative: Use GitHub CLI

If you have GitHub CLI installed:
```bash
# Create repositories
gh repo create trading-system-frontend --public --description "Angular 17 frontend for 10-Agent Trading System"
gh repo create trading-system-backend --public --description "Spring Boot 3.2 backend for 10-Agent Trading System"
gh repo create trading-system-infrastructure --public --description "Docker infrastructure for 10-Agent Trading System"

# Push code
cd frontend && git init && git add . && git commit -m "Initial commit" && git branch -M main && git remote add origin https://github.com/YOUR_USERNAME/trading-system-frontend.git && git push -u origin main
cd ../backend && git init && git add . && git commit -m "Initial commit" && git branch -M main && git remote add origin https://github.com/YOUR_USERNAME/trading-system-backend.git && git push -u origin main
cd .. && git init && git add . && git commit -m "Initial commit" && git branch -M main && git remote add origin https://github.com/YOUR_USERNAME/trading-system-infrastructure.git && git push -u origin main
```

## Repository URLs After Creation:
- Frontend: `https://github.com/YOUR_USERNAME/trading-system-frontend`
- Backend: `https://github.com/YOUR_USERNAME/trading-system-backend`
- Infrastructure: `https://github.com/YOUR_USERNAME/trading-system-infrastructure`

**Note**: Replace `YOUR_USERNAME` with your actual GitHub username.