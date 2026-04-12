# Daily Trading Recommendation Script
# Generates a new trading recommendation

# Get current date and time
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.ffffff"

# Sample stock symbols to choose from
$symbols = @("AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK.B", "JPM", "V")

# Randomly select a symbol
$random = Get-Random -Minimum 0 -Maximum $symbols.Count
$symbol = $symbols[$random]

# Generate random signal (BUY/SELL/HOLD)
$signals = @("BUY", "SELL", "HOLD")
$signal = $signals[(Get-Random -Minimum 0 -Maximum $signals.Count)]

# Generate random confidence (50-95%)
$confidence = Get-Random -Minimum 50 -Maximum 96

# Generate price data
$currentPrice = [math]::Round((Get-Random -Minimum 100 -Maximum 500), 2)
$priceTarget = [math]::Round($currentPrice * (1 + (Get-Random -Minimum -0.05 -Maximum 0.15)), 4)
$stopLoss = [math]::Round($currentPrice * (1 - (Get-Random -Minimum 0.02 -Maximum 0.1)), 4)

# Calculate metrics
$potentialReturnPct = [math]::Round((($priceTarget - $currentPrice) / $currentPrice) * 100, 2)
$riskRewardRatio = [math]::Round(($priceTarget - $currentPrice) / ($currentPrice - $stopLoss), 4)

# Reasons based on signal
$reasons = @{
    "BUY" = @("Strong technical breakout", "Positive earnings outlook", "Institutional accumulation", "Oversold bounce expected")
    "SELL" = @("Technical resistance reached", "Profit taking opportunity", "Overbought conditions", "Negative sector rotation")
    "HOLD" = @("Awaiting catalyst", "Consolidation phase", "Mixed signals", "Neutral market conditions")
}

$reason = $reasons[$signal][(Get-Random -Minimum 0 -Maximum $reasons[$signal].Count)]

# Create recommendation object
$recommendation = @{
    symbol = $symbol
    signal = $signal
    confidence = $confidence
    reason = $reason
    price_target = $priceTarget
    stop_loss = $stopLoss
    current_price = $currentPrice
    potential_return_pct = $potentialReturnPct
    risk_reward_ratio = $riskRewardRatio
    timestamp = $timestamp
}

# Convert to JSON and save
$recommendation | ConvertTo-Json | Out-File -FilePath "C:\Users\pcnsl\.openclaw\workspace\first_recommendation.json" -Encoding UTF8

Write-Host "Daily recommendation generated for $symbol : $signal (Confidence: ${confidence}%)"
Write-Host "Saved to first_recommendation.json"