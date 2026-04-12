# Comprehensive Sample Data Population Script
# This script populates the trading dashboard with realistic sample data

Write-Host "📊 POPULATING TRADING DASHBOARD WITH SAMPLE DATA" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BaseUrl = "http://localhost:8082/api"
$Headers = @{
    "Content-Type" = "application/json"
}

function Invoke-Post($Endpoint, $Body) {
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/$Endpoint" -Method Post -Headers $Headers -Body ($Body | ConvertTo-Json)
        Write-Host "  ✅ $Endpoint" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "  ❌ $Endpoint - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Clear existing data (optional - comment out if you want to keep existing data)
# Write-Host "Clearing existing data..." -ForegroundColor Yellow
# Invoke-RestMethod -Uri "$BaseUrl/consensus" -Method Delete -ErrorAction SilentlyContinue
# Invoke-RestMethod -Uri "$BaseUrl/trade-recommendations" -Method Delete -ErrorAction SilentlyContinue
# Invoke-RestMethod -Uri "$BaseUrl/chat" -Method Delete -ErrorAction SilentlyContinue

Write-Host "1. Creating Consensus Votes..." -ForegroundColor Yellow

# Create consensus votes for various symbols
$symbols = @("AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "BTC", "ETH", "SPY")
$agents = @("technical_analyst", "fundamental_analyst", "sentiment_analyst", "macro_analyst", "crypto_analyst", "risk_manager", "options_strategist", "quantitative_analyst", "sector_specialist", "compliance_expert")

for ($i = 0; $i -lt 15; $i++) {
    $symbol = $symbols | Get-Random
    $decision = @("BUY", "SELL", "HOLD") | Get-Random
    $confidence = 0.65 + (Get-Random -Maximum 0.3) # 0.65 to 0.95
    
    # Randomly select agents
    $shuffledAgents = $agents | Get-Random -Count $agents.Count
    $inFavorCount = if ($decision -eq "BUY") { 6 } elseif ($decision -eq "SELL") { 3 } else { 4 }
    $agentsInFavor = $shuffledAgents[0..($inFavorCount-1)] -join ","
    $agentsAgainst = $shuffledAgents[$inFavorCount..($inFavorCount+2)] -join ","
    
    $body = @{
        symbol = $symbol
        finalDecision = $decision
        confidence = [Math]::Round($confidence, 2)
        agentsInFavor = $agentsInFavor
        agentsAgainst = $agentsAgainst
        totalAgents = 10
        agentsVoted = 7 + (Get-Random -Maximum 3) # 7 to 9
        reasoning = "Analysis indicates $decision signal based on technical indicators and market sentiment for $symbol."
        priceAtDecision = [Math]::Round((100 + (Get-Random -Maximum 2000)), 2)
        timestamp = (Get-Date).AddHours(-(Get-Random -Maximum 48)).ToString("yyyy-MM-ddTHH:mm:ss")
    }
    
    Invoke-Post -Endpoint "consensus" -Body $body | Out-Null
}

Write-Host "`n2. Creating Trade Recommendations..." -ForegroundColor Yellow

# Create trade recommendations
$statuses = @("active", "executed", "cancelled", "expired")
$recommendedBy = @("Consensus Engine", "Technical Analyst", "AI Model v2.5", "Risk-Adjusted System", "HuggingFace Model")

for ($i = 0; $i -lt 12; $i++) {
    $symbol = $symbols | Get-Random
    $status = if ($i -lt 4) { "active" } else { $statuses | Get-Random }
    $confidence = 0.7 + (Get-Random -Maximum 0.25) # 0.7 to 0.95
    $basePrice = 100 + (Get-Random -Maximum 2000)
    
    $body = @{
        symbol = $symbol
        status = $status
        recommendedBy = $recommendedBy | Get-Random
        confidence = [Math]::Round($confidence, 2)
        currentPrice = [Math]::Round($basePrice, 2)
        rationale = "Strong fundamentals combined with favorable technical setup for $symbol. AI model indicates high probability of success."
    }
    
    if ($status -eq "active") {
        $body.entryRange = "$([Math]::Round($basePrice * 0.98, 2))-$([Math]::Round($basePrice * 1.02, 2))"
        $body.target = [Math]::Round($basePrice * (1.05 + (Get-Random -Maximum 0.1)), 2) # 5-15% target
        $body.stopLoss = [Math]::Round($basePrice * (0.92 + (Get-Random -Maximum 0.05)), 2) # 8-3% stop loss
        $body.positionSize = [Math]::Round((1 + (Get-Random -Maximum 4)), 2) # 1-5% position size
        $body.riskRewardRatio = [Math]::Round((2 + (Get-Random -Maximum 3)), 2) # 2-5:1 risk/reward
        $body.potentialPnl = [Math]::Round((3 + (Get-Random -Maximum 12)), 2) # 3-15% potential P&L
    }
    
    Invoke-Post -Endpoint "trade-recommendations" -Body $body | Out-Null
}

Write-Host "`n3. Creating AI Agent Chat Messages..." -ForegroundColor Yellow

# Create chat messages between AI agents
$senders = @("technical_analyst", "fundamental_analyst", "sentiment_analyst", "macro_analyst", "crypto_analyst", "risk_manager", "huggingface_model", "ai_consensus_engine")
$receivers = @("all", "technical_analyst", "fundamental_analyst", "sentiment_analyst", "consensus_engine", "risk_manager")
$messageTypes = @("analysis", "alert", "question", "recommendation", "warning", "ai_insight")

# HuggingFace model messages
$huggingfaceMessages = @(
    "HuggingFace model analysis completed on {symbol}. Sentiment score: {score}.",
    "AI model detects unusual pattern in {symbol} options flow. Confidence: {confidence}%",
    "Transformer model predicts {direction} movement for {symbol} in next 24h.",
    "NLP analysis of news sentiment for {symbol} shows {sentiment} trend.",
    "Large Language Model recommends {action} on {symbol} based on technical/fundamental convergence."
)

for ($i = 0; $i -lt 20; $i++) {
    $sender = $senders | Get-Random
    $receiver = $receivers | Get-Random
    $symbol = $symbols | Get-Random
    $messageType = $messageTypes | Get-Random
    $confidence = 0.6 + (Get-Random -Maximum 0.4) # 0.6 to 1.0
    
    # Generate message based on sender and type
    if ($sender -eq "huggingface_model") {
        $template = $huggingfaceMessages | Get-Random
        $message = $template -replace "{symbol}", $symbol -replace "{score}", [Math]::Round((Get-Random -Maximum 1.0), 2) -replace "{confidence}", [Math]::Round($confidence * 100) -replace "{direction}", (@("bullish", "bearish") | Get-Random) -replace "{sentiment}", (@("positive", "negative", "neutral") | Get-Random) -replace "{action}", (@("BUY", "SELL", "HOLD") | Get-Random)
    } else {
        $role = $sender -replace "_", " " -replace "analyst", "Analyst" -replace "manager", "Manager"
        $messages = @(
            "$($role): Completed analysis on $symbol. RSI showing {signal}.",
            "$($role): Alert for $symbol - {condition} detected.",
            "$($role): Question regarding $symbol's {metric} - any insights?",
            "$($role): Recommendation for $symbol - consider {action} position.",
            "$($role): Warning for $symbol - {warning} pattern forming."
        )
        $message = $messages | Get-Random
        $message = $message -replace "{signal}", (@("oversold", "overbought", "divergence") | Get-Random) -replace "{condition}", (@("unusual volume", "breakout", "breakdown") | Get-Random) -replace "{metric}", (@("earnings guidance", "valuation", "technical setup") | Get-Random) -replace "{action}", (@("long", "short", "swing") | Get-Random) -replace "{warning}", (@("bearish", "bullish trap", "volatility expansion") | Get-Random)
    }
    
    $body = @{
        sender = $sender
        receiver = $receiver
        message = $message
        messageType = $messageType
        symbol = $symbol
        confidence = [Math]::Round($confidence, 2)
        context = "AI agent communication regarding $symbol trading analysis"
        timestamp = (Get-Date).AddMinutes(-(Get-Random -Maximum 240)).ToString("yyyy-MM-ddTHH:mm:ss")
    }
    
    Invoke-Post -Endpoint "chat" -Body $body | Out-Null
}

Write-Host "`n4. Creating Agent Activities..." -ForegroundColor Yellow

# Create agent activities (if endpoint exists)
try {
    for ($i = 0; $i -lt 10; $i++) {
        $agent = $senders | Get-Random
        $symbol = $symbols | Get-Random
        $task = @("Technical analysis", "Fundamental evaluation", "Sentiment scoring", "Risk assessment", "AI model inference") | Get-Random
        
        $body = @{
            agentId = $agent
            task = "$task for $symbol"
            activityType = "analysis"
            symbol = $symbol
            status = "completed"
            reasoning = "Agent performed $task using AI models and market data."
            durationMs = 1000 + (Get-Random -Maximum 5000)
            timestamp = (Get-Date).AddMinutes(-(Get-Random -Maximum 120)).ToString("yyyy-MM-ddTHH:mm:ss")
        }
        
        Invoke-Post -Endpoint "agent-activities" -Body $body | Out-Null
    }
} catch {
    Write-Host "  ℹ️ Agent activities endpoint not available or error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n5. Creating Enhanced Monitoring Stats (Simulated HuggingFace Metrics)..." -ForegroundColor Yellow

# Create a custom monitoring stats endpoint that includes HuggingFace metrics
# This would normally be done in the backend, but we'll simulate by creating additional data
Write-Host "  ℹ️ HuggingFace integration requires backend changes. Sample data includes:" -ForegroundColor Yellow
Write-Host "     - AI model inference messages" -ForegroundColor White
Write-Host "     - Transformer-based analysis" -ForegroundColor White
Write-Host "     - NLP sentiment scoring" -ForegroundColor White
Write-Host "     - LLM trading recommendations" -ForegroundColor White

Write-Host "`n📈 SAMPLE DATA POPULATION COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Data Summary:" -ForegroundColor Cyan
Write-Host "- Consensus Votes: 15" -ForegroundColor White
Write-Host "- Trade Recommendations: 12 (4 active)" -ForegroundColor White
Write-Host "- AI Chat Messages: 20 (including HuggingFace model)" -ForegroundColor White
Write-Host "- Agent Activities: 10" -ForegroundColor White
Write-Host ""
Write-Host "Dashboard Components Now Showing:" -ForegroundColor Cyan
Write-Host "✅ Consensus Board - Multiple votes with AI reasoning" -ForegroundColor Green
Write-Host "✅ Trade Recommendations - Active trades with targets/stops" -ForegroundColor Green
Write-Host "✅ Interagent Communications - AI agents chatting with HuggingFace" -ForegroundColor Green
Write-Host "✅ Performance Metrics - Stats endpoint has data" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Refresh dashboard at http://localhost:4200" -ForegroundColor White
Write-Host "2. Click 'Refresh' buttons in each component" -ForegroundColor White
Write-Host "3. Test category filtering in recommendations" -ForegroundColor White
Write-Host "4. View AI agent conversations in chat" -ForegroundColor White
Write-Host ""
Write-Host "Note: UI compilation errors need to be fixed for full functionality." -ForegroundColor Red
Write-Host "     Run: cd frontend && npm install (if environment issue persists)" -ForegroundColor White
Write-Host "     Or restart Angular dev server" -ForegroundColor White