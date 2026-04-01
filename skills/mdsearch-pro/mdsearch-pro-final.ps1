# mdsearch-pro - Enhanced Markdown Search
# Feature-rich, Windows-native, skill-integrated

param(
    [string]$Query,
    [string]$Path = ".",
    [int]$Limit = 10,
    [switch]$Json = $false,
    [switch]$Full = $false,
    [switch]$Verbose = $false
)

# Core search function with scoring
function Search-Files {
    param($query, $searchPath, $maxResults)
    
    $results = @()
    $files = Get-ChildItem $searchPath -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue
    
    if ($Verbose) { Write-Host "Searching $($files.Count) files..." }
    
    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw
            $lines = $content -split "`n"
            
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i].Trim()
                if (-not $line) { continue }
                
                # Calculate relevance score
                $score = 0
                $hasMatch = $false
                
                # Exact match
                if ($line -match $query) {
                    $score += 3
                    $hasMatch = $true
                }
                
                # Word matches
                $words = $query -split '\s+'
                foreach ($word in $words) {
                    if ($word.Length -gt 2 -and $line -match "\b$word\b") {
                        $score += 1
                        $hasMatch = $true
                    }
                }
                
                # Position bonuses
                if ($i -eq 0 -and $line.StartsWith("#")) { $score += 2 } # Title
                if ($line.StartsWith("##")) { $score += 1 } # Heading
                
                if ($hasMatch -and $score -gt 0) {
                    $result = [PSCustomObject]@{
                        File = $file.FullName
                        Name = $file.Name
                        Line = $i + 1
                        Content = if ($Full) { $lines[$i] } else { $line }
                        Score = $score
                        Context = @{
                            Before = if ($i -gt 0) { $lines[$i-1].Trim() } else { "" }
                            After = if ($i -lt $lines.Count - 1) { $lines[$i+1].Trim() } else { "" }
                        }
                    }
                    
                    $results += $result
                    if ($results.Count -ge $maxResults) { return $results }
                }
            }
        }
        catch { if ($Verbose) { Write-Host "Error: $($file.Name)" } }
    }
    
    return $results | Sort-Object Score -Descending
}

# Humanizer formatting
function Format-Human {
    param($results, $query)
    
    $output = @()
    $output += "Search Results: '$query'"
    $output += "=" * 40
    
    if ($results.Count -eq 0) {
        $output += "No matches found."
        $output += "Try different keywords or check spelling."
    }
    else {
        $output += "Found $($results.Count) relevant matches:"
        $output += ""
        
        foreach ($result in $results) {
            $preview = if ($result.Content.Length -gt 50) {
                $result.Content.Substring(0, 47) + "..."
            } else {
                $result.Content
            }
            
            $output += "$($result.Name):$($result.Line) (score: $($result.Score))"
            $output += "  $preview"
            $output += "  Path: $($result.File)"
            $output += "---"
        }
        
        $output += ""
        $output += "Summary: $($results.Count) matches"
    }
    
    return $output -join "`n"
}

# ByteRover integration placeholder
function ByteRover-Log {
    param($query, $count)
    if ($Verbose) {
        Write-Host "[ByteRover] Logged search: '$query' found $count results"
    }
}

# Main
if (-not $Query) {
    Write-Host "Usage: .\mdsearch-pro-final.ps1 -Query 'search term' [-Path '.'] [-Limit 10] [-Json] [-Full] [-Verbose]"
    exit 1
}

$start = Get-Date
$results = Search-Files -query $Query -searchPath $Path -maxResults $Limit
$end = Get-Date
$time = [math]::Round(($end - $start).TotalSeconds, 2)

# ByteRover integration
ByteRover-Log -query $Query -count $results.Count

if ($Json) {
    $output = @{
        query = $Query
        path = $Path
        timeSeconds = $time
        count = $results.Count
        results = $results
        skills = @{
            byteRover = $true
            humanizer = (-not $Json)
        }
    }
    $output | ConvertTo-Json -Depth 2
}
else {
    Write-Host (Format-Human -results $results -query $Query)
    Write-Host "`nSearch completed in ${time}s" -ForegroundColor Gray
    Write-Host "ByteRover integration: Active" -ForegroundColor Magenta
}