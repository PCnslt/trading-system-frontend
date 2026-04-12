param([string]$prompt, [string]$model = "llama3.2:3b")

$tempFile = ".\research\temp_output.txt"
# Write prompt to a file
$prompt | Out-File -FilePath ".\research\temp_prompt.txt" -Encoding utf8

# Start ollama process
$process = Start-Process -FilePath "ollama" -ArgumentList "run", $model -RedirectStandardInput ".\research\temp_prompt.txt" -RedirectStandardOutput $tempFile -NoNewWindow -PassThru

# Wait for process with timeout (30 seconds)
$timeout = 30
$process | Wait-Process -Timeout $timeout -ErrorAction SilentlyContinue
if (!$process.HasExited) {
    $process | Stop-Process -Force
    Write-Host "Process timed out after $timeout seconds."
}

# Read output
if (Test-Path $tempFile) {
    Get-Content $tempFile -Raw
} else {
    Write-Host "No output generated."
}