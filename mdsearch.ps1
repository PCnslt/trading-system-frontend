# Simple markdown search for Windows
# Usage: .\mdsearch.ps1 "search term"

param([string]$term = $(throw "Search term required"))

if (-not $term) {
    Write-Host "Usage: .\mdsearch.ps1 'search term'"
    exit 1
}

Write-Host "Searching for: $term"
Write-Host ""

$files = Get-ChildItem -Path . -Filter "*.md" -Recurse -File
$count = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $lines = $content -split "`n"
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $term) {
            $count++
            Write-Host "[$count] $($file.Name):$($i+1)"
            Write-Host "     $($lines[$i].Trim())"
            Write-Host ""
        }
    }
}

Write-Host "Found $count matches"