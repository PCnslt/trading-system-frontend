#!/usr/bin/env pwsh
<#
Daily Billionaire Trading Recommendation
Runs stock analysis and sends to WhatsApp
#>

$ErrorActionPreference = "Stop"

# Configuration
$Workspace = "C:\Users\pcnsl\.openclaw\workspace"
$PythonScript = "first_recommendation.py"
$OutputFile = "first_recommendation.json"
$WhatsAppNumber = "+17038519152"  # User's WhatsApp number

# Change to workspace
Set-Location $Workspace

Write-Host "Starting daily billionaire recommendation..." -ForegroundColor Cyan

# Run Python script
Write-Host "Running stock analysis..." -ForegroundColor Yellow
python $PythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Python script failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Check if output file exists
if (-not (Test-Path $OutputFile)) {
    Write-Host "Output file not found: $OutputFile" -ForegroundColor Red
    exit 1
}

# Read and parse JSON
$recommendation = Get-Content $OutputFile | ConvertFrom-Json

# Format message
$symbol = $recommendation.symbol
$signal = $recommendation.signal
$confidence = $recommendation.confidence
$reason = $recommendation.reason
$currentPrice = $recommendation.current_price
$priceTarget = $recommendation.price_target
$stopLoss = $recommendation.stop_loss

$potentialReturn = if ($recommendation.potential_return_pct) { $recommendation.potential_return_pct } else { 0 }
$riskReward = if ($recommendation.risk_reward_ratio) { $recommendation.risk_reward_ratio } else { 0 }

$message = @"
💰 *DAILY BILLIONAIRE RECOMMENDATION*

*Stock:* $symbol
*Signal:* $signal
*Confidence:* $confidence%

*Current Price:* `$$currentPrice
*Price Target:* `$$priceTarget
*Stop Loss:* `$$stopLoss

*Potential Return:* $potentialReturn%
*Risk/Reward:* $riskReward`:1

*Reason:* $reason

*Time:* $(Get-Date -Format "yyyy-MM-dd HH:mm")
*System:* 10-Agent Trading AI (Building)

---
_This is an automated recommendation. Past performance is not indicative of future results. Trading involves risk._
"@

Write-Host "Recommendation generated:" -ForegroundColor Green
Write-Host $message

# Send to WhatsApp
Write-Host "Sending to WhatsApp..." -ForegroundColor Cyan

try {
    # Use OpenClaw message tool
    # Note: This requires OpenClaw context; will be called from cron job
    # The cron job's agent session will handle messaging
    # For now, just output
    Write-Host "[SIMULATED] WhatsApp message ready for delivery"
    Write-Host "   To: $WhatsAppNumber"
    
    # In actual cron job, we would call:
    # openclaw message send --channel whatsapp --to $WhatsAppNumber --message $message
    
} catch {
    Write-Host "Failed to send WhatsApp message: $_" -ForegroundColor Yellow
}

# Save for dashboard
$dashboardFile = "daily-recommendation-$(Get-Date -Format 'yyyy-MM-dd').json"
$recommendation | Add-Member -NotePropertyName "whatsapp_sent" -NotePropertyValue (Get-Date -Format "o") -Force
$recommendation | ConvertTo-Json -Depth 10 | Set-Content $dashboardFile

Write-Host "Saved to: $dashboardFile" -ForegroundColor Green
Write-Host "Daily recommendation complete!" -ForegroundColor Green