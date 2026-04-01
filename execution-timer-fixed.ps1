# Execution Timer Functions
# Created: March 30, 2026

$executionLog = "C:\Users\pcnsl\.openclaw\workspace\execution-log.json"
$currentTask = $null
$taskStartTime = $null

function Start-ExecutionTimer {
    param(
        [string]$Task,
        [int]$Minutes = 15
    )
    
    $global:currentTask = @{
        Name = $Task
        StartTime = Get-Date
        TimeLimit = $Minutes
        Status = "Running"
    }
    
    $global:taskStartTime = Get-Date
    
    Write-Host "🚀 Starting: $Task" -ForegroundColor Green
    Write-Host "⏰ Time limit: $Minutes minutes" -ForegroundColor Yellow
    Write-Host "⏱️  Started at: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
    
    # Log the start
    $logEntry = @{
        Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        Action = "Start"
        Task = $Task
        TimeLimit = $Minutes
    }
    
    $logData = @()
    if (Test-Path $executionLog) {
        $logData = Get-Content $executionLog | ConvertFrom-Json
    }
    
    $logData += $logEntry
    $logData | ConvertTo-Json | Set-Content $executionLog
    
    return $global:currentTask
}

function Get-ExecutionStatus {
    if (-not $global:currentTask) {
        Write-Host "📭 No active task" -ForegroundColor Gray
        return
    }
    
    $elapsed = (Get-Date) - $global:taskStartTime
    $minutesElapsed = [math]::Round($elapsed.TotalMinutes, 1)
    $minutesLeft = $global:currentTask.TimeLimit - $minutesElapsed
    
    Write-Host "📊 Current Task: $($global:currentTask.Name)" -ForegroundColor Cyan
    Write-Host "⏱️  Elapsed: $minutesElapsed minutes" -ForegroundColor Yellow
    Write-Host "⏳ Remaining: $minutesLeft minutes" -ForegroundColor $(if ($minutesLeft -lt 2) { "Red" } else { "Green" })
    Write-Host "📈 Progress: $(Get-ProgressBar $minutesElapsed $global:currentTask.TimeLimit)" -ForegroundColor Magenta
    
    if ($minutesLeft -le 0) {
        Write-Host "⏰ TIME'S UP! Move to next task or extend." -ForegroundColor Red -BackgroundColor Black
    }
    
    return @{
        Task = $global:currentTask.Name
        ElapsedMinutes = $minutesElapsed
        RemainingMinutes = $minutesLeft
        Status = if ($minutesLeft -le 0) { "Overdue" } else { "OnTrack" }
    }
}

function Get-ProgressBar {
    param($Current, $Total, $Width = 20)
    
    $percentage = [math]::Min(100, [math]::Round(($Current / $Total) * 100))
    $filled = [math]::Round(($percentage / 100) * $Width)
    $empty = $Width - $filled
    
    $bar = "█" * $filled + "░" * $empty
    return "$bar $percentage%"
}

function Complete-Task {
    param([string]$Result = "Completed")
    
    if (-not $global:currentTask) {
        Write-Host "❌ No active task to complete" -ForegroundColor Red
        return
    }
    
    $elapsed = (Get-Date) - $global:taskStartTime
    $minutesElapsed = [math]::Round($elapsed.TotalMinutes, 2)
    
    Write-Host "✅ Task Completed: $($global:currentTask.Name)" -ForegroundColor Green
    Write-Host "⏱️  Time spent: $minutesElapsed minutes" -ForegroundColor Cyan
    Write-Host "📝 Result: $Result" -ForegroundColor Yellow
    
    # Log completion
    $logEntry = @{
        Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        Action = "Complete"
        Task = $global:currentTask.Name
        TimeSpent = $minutesElapsed
        Result = $Result
    }
    
    $logData = @()
    if (Test-Path $executionLog) {
        $logData = Get-Content $executionLog | ConvertFrom-Json
    }
    
    $logData += $logEntry
    $logData | ConvertTo-Json | Set-Content $executionLog
    
    $global:currentTask = $null
    $global:taskStartTime = $null
}

function Next-Task {
    param([string]$Reason = "Moving to next task")
    
    if ($global:currentTask) {
        Write-Host "⏭️  Skipping: $($global:currentTask.Name)" -ForegroundColor Yellow
        Write-Host "📝 Reason: $Reason" -ForegroundColor Gray
        
        # Log skip
        $logEntry = @{
            Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            Action = "Skip"
            Task = $global:currentTask.Name
            Reason = $Reason
        }
        
        $logData = @()
        if (Test-Path $executionLog) {
            $logData = Get-Content $executionLog | ConvertFrom-Json
        }
        
        $logData += $logEntry
        $logData | ConvertTo-Json | Set-Content $executionLog
    }
    
    $global:currentTask = $null
    $global:taskStartTime = $null
    Write-Host "🔄 Ready for next task" -ForegroundColor Green
}

# Initialize execution log if it doesn't exist
if (-not (Test-Path $executionLog)) {
    @() | ConvertTo-Json | Set-Content $executionLog
}

Write-Host "⚡ Execution Timer loaded" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  Start-ExecutionTimer -Task 'Task Name' -Minutes 15" -ForegroundColor White
Write-Host "  Get-ExecutionStatus" -ForegroundColor White
Write-Host "  Complete-Task -Result 'Success'" -ForegroundColor White
Write-Host "  Next-Task -Reason 'Time limit reached'" -ForegroundColor White