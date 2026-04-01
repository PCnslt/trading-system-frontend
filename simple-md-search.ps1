# Simple Markdown Search for Windows
# Free, native PowerShell solution

param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    
    [string]$Path = ".",
    [int]$Limit = 10,
    [switch]$Recursive = $true
)

# Search function
function Search-MarkdownFiles {
    param($searchPath, $searchTerm, $maxResults)
    
    $results = @()
    $files = Get-ChildItem -Path $searchPath -Filter "*.md" -Recurse:$Recursive -File
    
    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw -ErrorAction Stop
            $lines = $content -split "`n"
            
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i].Trim()
                if ($line -match $searchTerm) {
                    $result = [PSCustomObject]@{
                        File = $file.FullName
                        LineNumber = $i + 1
                        Content = $line
                        Score = 1.0
                    }
                    $results += $result
                    
                    if ($results.Count -ge $maxResults) {
                        return $results
                    }
                }
            }
        }
        catch {
            Write-Warning "Could not read file: $($file.FullName)"
        }
    }
    
    return $results
}

# Main execution
Write-Host "`n🔍 Searching markdown files for: '$Query'" -ForegroundColor Cyan
Write-Host "Path: $Path" -ForegroundColor Gray
Write-Host "Limit: $Limit results" -ForegroundColor Gray
Write-Host ""

$startTime = Get-Date
$searchResults = Search-MarkdownFiles -searchPath $Path -searchTerm $Query -maxResults $Limit
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

if ($searchResults.Count -eq 0) {
    Write-Host "❌ No results found." -ForegroundColor Red
} else {
    Write-Host "✅ Found $($searchResults.Count) result(s) in ${duration}s" -ForegroundColor Green
    Write-Host ""
    
    foreach ($result in $searchResults) {
        Write-Host "📄 $(Split-Path $result.File -Leaf)" -ForegroundColor Yellow
        Write-Host "   Path: $($result.File)" -ForegroundColor Gray
        Write-Host "   Line $($result.LineNumber): $($result.Content)" -ForegroundColor White
        Write-Host "---"
    }
}

Write-Host "Tip: Use -Path to specify directory, -Limit for more/fewer results" -ForegroundColor Gray