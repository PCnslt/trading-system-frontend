# Windows Markdown Search
# Simple PowerShell-based markdown search for Windows

param(
    [string]$Query,
    [string]$Path = ".",
    [int]$Limit = 10,
    [switch]$Recursive = $true,
    [switch]$CaseSensitive = $false,
    [switch]$Json = $false
)

function Search-Markdown {
    param($searchPath, $searchQuery, $maxResults)
    
    $results = @()
    $pattern = "*.md"
    
    if ($Recursive) {
        $files = Get-ChildItem -Path $searchPath -Filter $pattern -Recurse -File
    } else {
        $files = Get-ChildItem -Path $searchPath -Filter $pattern -File
    }
    
    $caseOption = if ($CaseSensitive) { "" } else { "-CaseSensitive:$false" }
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        $lines = $content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($line -match $searchQuery $caseOption) {
                $result = @{
                    file = $file.FullName
                    line_number = $i + 1
                    line = $line.Trim()
                    score = 1.0  # Simple matching score
                }
                $results += $result
                
                if ($results.Count -ge $maxResults) {
                    break
                }
            }
        }
        
        if ($results.Count -ge $maxResults) {
            break
        }
    }
    
    return $results
}

# Main execution
if (-not $Query) {
    Write-Host "Usage: .\windows-markdown-search.ps1 -Query 'search term' [-Path '.'] [-Limit 10] [-Recursive] [-CaseSensitive] [-Json]"
    exit 1
}

$searchResults = Search-Markdown -searchPath $Path -searchQuery $Query -maxResults $Limit

if ($Json) {
    $searchResults | ConvertTo-Json -Depth 2
} else {
    Write-Host "`n🔍 Markdown Search Results for: '$Query'"
    Write-Host "=========================================="
    
    if ($searchResults.Count -eq 0) {
        Write-Host "No results found."
    } else {
        foreach ($result in $searchResults) {
            Write-Host "`n📄 File: $($result.file)"
            Write-Host "📝 Line $($result.line_number): $($result.line)"
            Write-Host "---"
        }
        Write-Host "`nFound $($searchResults.Count) result(s)"
    }
}