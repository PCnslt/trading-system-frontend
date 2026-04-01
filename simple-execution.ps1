# Simple Execution Timer
# Created: March 30, 2026

$executionLog = "C:\Users\pcnsl\.openclaw\workspace\execution-log.json"
$currentTask = $null
$taskStartTime = $null

function Start-Task {
    param([string]$Task, [int]$Minutes = 15)
    
    $global:currentTask = @{
        Name = $Task
        StartTime = Get-Date
        TimeLimit = $Minutes
    }
    
    $global:taskStartTime = Get-Date
    
    Write-Host "Starting: $Task"
    Write-Host "Time limit: $Minutes minutes"
    Write-Host "Started at: $(Get-Date -Format 'HH:mm:ss')"
    
    # Log
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
}

function Check-Status {
    if (-not $global:currentTask) {
        Write-Host "No active task"
        return
    }
    
    $elapsed = (Get-Date) - $global:taskStartTime
    $minutesElapsed = [math]::Round($elapsed.TotalMinutes, 1)
    $minutesLeft = $global:currentTask.TimeLimit - $minutesElapsed
    
    Write-Host "Current Task: $($global:currentTask.Name)"
    Write-Host "Elapsed: $minutesElapsed minutes"
    Write-Host "Remaining: $minutesLeft minutes"
    
    if ($minutesLeft -le 0) {
        Write-Host "TIME'S UP!"
    }
}

function End-Task {
    param([string]$Result = "Completed")
    
    if (-not $global:currentTask) {
        Write-Host "No active task"
        return
    }
    
    $elapsed = (Get-Date) - $global:taskStartTime
    $minutesElapsed = [math]::Round($elapsed.TotalMinutes, 2)
    
    Write-Host "Task Completed: $($global:currentTask.Name)"
    Write-Host "Time spent: $minutesElapsed minutes"
    
    # Log
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

# Initialize
if (-not (Test-Path $executionLog)) {
    @() | ConvertTo-Json | Set-Content $executionLog
}

Write-Host "Execution Timer loaded"
Write-Host "Commands: Start-Task, Check-Status, End-Task"