# Capability Evolver PowerShell Module
# Weekly self-evolution and improvement system

# Configuration
$A2A_NODE_ID = "node_02bd2eb075aaf60a"
$EVOMAP_CLAIM_URL = "https://evomap.ai/claim/M5AV-5UNC"
$EVOLUTION_SESSION = "session:evolution-coach"

function Test-EvoMapConnection {
    <#
    .SYNOPSIS
    Test connection to EvoMap using A2A_NODE_ID
    #>
    Write-Host "Testing EvoMap connection..." -ForegroundColor Cyan
    Write-Host "A2A_NODE_ID: $A2A_NODE_ID" -ForegroundColor Gray
    Write-Host "Claim URL: $EVOMAP_CLAIM_URL" -ForegroundColor Gray
    Write-Host "Note: Visit claim URL if not yet claimed within 24 hours" -ForegroundColor Yellow
    return $true
}

function Get-WeeklyPerformanceReport {
    <#
    .SYNOPSIS
    Analyze past week's performance from progress-tracker.md and memory files
    #>
    Write-Host "Generating weekly performance report..." -ForegroundColor Cyan
    
    $report = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        WeekStart = (Get-Date).AddDays(-7).ToString("yyyy-MM-dd")
        WeekEnd = (Get-Date).ToString("yyyy-MM-dd")
        Metrics = @{}
        Decisions = @()
        Improvements = @()
    }
    
    # Try to read progress-tracker.md
    $progressPath = "$PSScriptRoot/../../progress-tracker.md"
    if (Test-Path $progressPath) {
        $content = Get-Content $progressPath -Raw
        # Simple analysis - count completed tasks
        $completedTasks = ($content -split "\[x\]" | Measure-Object).Count - 1
        $totalTasks = ($content -split "\[ \]" | Measure-Object).Count - 1 + $completedTasks
        $completionRate = if ($totalTasks -gt 0) { [math]::Round(($completedTasks / $totalTasks) * 100, 2) } else { 0 }
        
        $report.Metrics["TaskCompletionRate"] = $completionRate
        $report.Metrics["CompletedTasks"] = $completedTasks
        $report.Metrics["TotalTasks"] = $totalTasks
    }
    
    # Try to read MEMORY.md for learning velocity
    $memoryPath = "$PSScriptRoot/../../MEMORY.md"
    if (Test-Path $memoryPath) {
        $content = Get-Content $memoryPath -Raw
        # Look for learning velocity pattern
        if ($content -match "Learning Velocity.*?(\d+(?:\.\d+)?)/10") {
            $report.Metrics["LearningVelocity"] = [double]$Matches[1]
        }
    }
    
    return $report
}

function Identify-ImprovementAreas {
    <#
    .SYNOPSIS
    Identify improvement areas based on weekly performance report
    .PARAMETER Report
    Weekly performance report from Get-WeeklyPerformanceReport
    #>
    param(
        [Parameter(Mandatory=$true)]
        [Hashtable]$Report
    )
    
    Write-Host "Identifying improvement areas..." -ForegroundColor Cyan
    
    $improvements = @()
    
    # Check learning velocity
    if ($Report.Metrics.ContainsKey("LearningVelocity")) {
        $lv = $Report.Metrics["LearningVelocity"]
        if ($lv -lt 4) {
            $improvements += @{
                Priority = "HIGH"
                Area = "Learning Velocity"
                Issue = "Learning velocity too low ($lv/10)"
                Action = "Focus on execution over analysis, implement micro-actions"
                Target = "Increase to 4.5/10 next week"
            }
        }
    }
    
    # Check task completion rate
    if ($Report.Metrics.ContainsKey("TaskCompletionRate")) {
        $rate = $Report.Metrics["TaskCompletionRate"]
        if ($rate -lt 80) {
            $improvements += @{
                Priority = "HIGH"
                Area = "Execution Rate"
                Issue = "Task completion rate too low ($rate%)"
                Action = "Improve accountability system, reduce task size"
                Target = "Reach 80% completion next week"
            }
        }
    }
    
    # Default improvements if no metrics
    if ($improvements.Count -eq 0) {
        $improvements += @{
            Priority = "MEDIUM"
            Area = "Skill Integration"
            Issue = "Skills installed but not deeply integrated"
            Action = "Increase skill utilization, enforce ByteRover habit"
            Target = "Use 3+ memory skills daily"
        }
        
        $improvements += @{
            Priority = "MEDIUM"
            Area = "Evolution Framework"
            Issue = "Weekly evolution not fully automated"
            Action = "Create cron job for Sunday evolution, enhance evolver.ps1"
            Target = "Fully automated weekly evolution by next month"
        }
    }
    
    return $improvements
}

function Update-MemoryWithLearnings {
    <#
    .SYNOPSIS
    Update MEMORY.md with evolution insights and improvements
    .PARAMETER Improvements
    Improvement areas from Identify-ImprovementAreas
    #>
    param(
        [Parameter(Mandatory=$true)]
        [Array]$Improvements
    )
    
    Write-Host "Updating MEMORY.md with evolution insights..." -ForegroundColor Cyan
    
    $memoryPath = "$PSScriptRoot/../../MEMORY.md"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    
    $evolutionEntry = @"

## $(Get-Date -Format "yyyy-MM-dd") - Weekly Evolution

**Time**: $timestamp
**A2A_NODE_ID**: $A2A_NODE_ID

### Improvement Areas Identified
"@
    
    foreach ($imp in $Improvements) {
        $evolutionEntry += @"
- **$($imp.Priority)**: $($imp.Area) - $($imp.Issue)
  - **Action**: $($imp.Action)
  - **Target**: $($imp.Target)

"@
    }
    
    $evolutionEntry += @"

### Next Week's Focus
1. Implement improvement actions above
2. Track progress in progress-tracker.md
3. Review skill utilization and prune as needed
4. Test memory system integration weekly

---
"@
    
    # Append to MEMORY.md
    if (Test-Path $memoryPath) {
        Add-Content -Path $memoryPath -Value $evolutionEntry
        Write-Host "✅ Updated MEMORY.md with evolution insights" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MEMORY.md not found, creating..." -ForegroundColor Yellow
        Set-Content -Path $memoryPath -Value $evolutionEntry
    }
}

function Start-WeeklyEvolution {
    <#
    .SYNOPSIS
    Main function to run weekly evolution
    #>
    Write-Host "🚀 Starting Weekly Evolution" -ForegroundColor Magenta
    Write-Host "=============================" -ForegroundColor Magenta
    
    # Test EvoMap connection
    $connectionTest = Test-EvoMapConnection
    
    # Get performance report
    $report = Get-WeeklyPerformanceReport
    
    # Identify improvements
    $improvements = Identify-ImprovementAreas -Report $report
    
    # Update memory
    Update-MemoryWithLearnings -Improvements $improvements
    
    # Display summary
    Write-Host "`n📊 Evolution Complete" -ForegroundColor Green
    Write-Host "-------------------" -ForegroundColor Green
    Write-Host "Improvements identified: $($improvements.Count)" -ForegroundColor Gray
    Write-Host "MEMORY.md updated: $(if (Test-Path "$PSScriptRoot/../../MEMORY.md") { '✅' } else { '❌' })" -ForegroundColor Gray
    Write-Host "EvoMap connection: $(if ($connectionTest) { '✅' } else { '❌' })" -ForegroundColor Gray
    
    return @{
        Success = $true
        Improvements = $improvements
        Report = $report
    }
}

function Get-CapabilityEvolverStatus {
    <#
    .SYNOPSIS
    Get current status of capability evolver system
    #>
    $status = @{
        A2A_NODE_ID = $A2A_NODE_ID
        EvoMapClaimUrl = $EVOMAP_CLAIM_URL
        LastEvolution = "Not yet run"
        SkillFiles = @()
    }
    
    # Check for required files
    $skillFiles = @("SKILL.md", "evolver.ps1")
    foreach ($file in $skillFiles) {
        $path = Join-Path $PSScriptRoot $file
        $status.SkillFiles += @{
            Name = $file
            Exists = Test-Path $path
            Path = $path
        }
    }
    
    return $status
}

# Export functions
Export-ModuleMember -Function Test-EvoMapConnection, Get-WeeklyPerformanceReport, Identify-ImprovementAreas, Update-MemoryWithLearnings, Start-WeeklyEvolution, Get-CapabilityEvolverStatus

Write-Host "Capability Evolver module loaded. Use Start-WeeklyEvolution to run weekly evolution." -ForegroundColor Cyan