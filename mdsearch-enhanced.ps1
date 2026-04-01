# mdsearch-enhanced - Professional Markdown Search
# Windows-native, skill-integrated, better than qmd

param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    
    [string]$Path = ".",
    [int]$Limit = 20,
    [switch]$Recursive = $true,
    [switch]$Json = $false,
    [switch]$Full = $false,
    [double]$MinScore = 0.1
)

# Configuration
$VERSION = "1.0.0"
$SKILLS = @{
    ByteRover = $true
    Humanizer = $true
}

# Search with scoring
function Search-Markdown {
    param($searchPath, $searchQuery, $maxResults, $minScore)
    
    $results = @()
    $files = Get-ChildItem -Path $searchPath -Filter "*.md" -Recurse:$Recursive -File
    
    Write-Host "Searching $($files.Count) markdown files..." -ForegroundColor Gray
    
    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw
            $lines = $content -split "`n"
            
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i].Trim()
                if (-not $line) { continue }
                
                # Calculate match score
                $score = 0.0
                $match = $false
                
                # Exact phrase match
                if ($line -match $searchQuery) {
                    $score += 2.0
                    $match = $true
                }
                
                # Individual word matches
                $words = $searchQuery -split '\s+' | Where-Object { $_.Length -gt 2 }
                foreach ($word in $words) {
                    if ($line -match "\b$word\b") {
                        $score += 0.5
                        $match = $true
                    }
                }
                
                # Boost for important positions
                if ($i -eq 0 -and $line -match "^#") { $score += 1.0 } # Title
                if ($line -match "^##") { $score += 0.5 } # Heading
                if ($line -match "^\s*[-*]") { $score += 0.3 } # List item
                
                if ($match -and $score -ge $minScore) {
                    $result = [PSCustomObject]@{
                        File = $file.FullName
                        FileName = $file.Name
                        LineNumber = $i + 1
                        Content = if ($Full) { $lines[$i] } else { $line }
                        Score = [math]::Round($score, 2)
                        Context = @{
                            Before = if ($i -gt 0) { $lines[$i-1].Trim() } else { "" }
                            After = if ($i -lt $lines.Count - 1) { $lines[$i+1].Trim() } else { "" }
                        }
                    }
                    
                    $results += $result
                    
                    if ($results.Count -ge $maxResults) {
                        break 2
                    }
                }
            }
        }
        catch {
            Write-Verbose "Error reading $($file.FullName)"
        }
    }
    
    # Sort by score
    return $results | Sort-Object Score -Descending
}

# Humanizer formatting
function Format-ResultsHumanized {
    param($results, $query)
    
    $output = @()
    $output += "SEARCH RESULTS: '$query'"
    $output += "=" * 50
    
    if ($results.Count -eq 0) {
        $output += "No matches found."
        $output += ""
        $output += "Suggestions:"
        $output += "- Try different keywords"
        $output += "- Check your spelling"
        $output += "- Search in a different location"
    }
    else {
        $output += "Found $($results.Count) relevant matches:"
        $output += ""
        
        $grouped = $results | Group-Object FileName
        foreach ($group in $grouped) {
            $filename = $group.Name
            $matches = $group.Group
            
            $output += "File: $filename"
            $output += "Path: $($matches[0].File)"
            $output += "Matches: $($matches.Count)"
            $output += ""
            
            foreach ($match in $matches | Select-Object -First 2) {
                $preview = if ($match.Content.Length -gt 60) {
                    $match.Content.Substring(0, 57) + "..."
                } else {
                    $match.Content
                }
                $output += "  Line $($match.LineNumber) (score: $($match.Score)): $preview"
            }
            
            if ($matches.Count -gt 2) {
                $output += "  ... and $($matches.Count - 2) more"
            }
            $output += "---"
        }
        
        $output += ""
        $output += "Summary: $($results.Count) matches across $($grouped.Count) files"
    }
    
    return $output -join "`n"
}

# ByteRover integration
function Invoke-ByteRoverSearch {
    param($query, $results)
    
    if ($SKILLS.ByteRover) {
        # Create search context for ByteRover
        $context = @{
            query = $query
            resultCount = $results.Count
            timestamp = (Get-Date).ToString("o")
            fileCount = ($results | Select-Object -Unique File).Count
        }
        
        # This would normally call brv curate
        Write-Verbose "[ByteRover] Search context: $($context | ConvertTo-Json -Compress)"
        return $context
    }
    return $null
}

# Main execution
$startTime = Get-Date
$searchResults = Search-Markdown -searchPath $Path -searchQuery $Query -maxResults $Limit -minScore $MinScore
$endTime = Get-Date
$duration = [math]::Round(($endTime - $startTime).TotalSeconds, 2)

# ByteRover integration
$byteRoverContext = Invoke-ByteRoverSearch -query $Query -results $searchResults

if ($Json) {
    $output = @{
        metadata = @{
            query = $Query
            path = $Path
            limit = $Limit
            recursive = $Recursive
            durationSeconds = $duration
            timestamp = (Get-Date).ToString("o")
            version = $VERSION
            skills = $SKILLS
            byteRover = $byteRoverContext
        }
        results = $searchResults
        summary = @{
            totalMatches = $searchResults.Count
            uniqueFiles = ($searchResults | Select-Object -Unique File).Count
            averageScore = if ($searchResults.Count -gt 0) { [math]::Round(($searchResults | Measure-Object Score -Average).Average, 2) } else { 0 }
        }
    }
    
    $output | ConvertTo-Json -Depth 3
}
else {
    # Humanized output
    if ($SKILLS.Humanizer) {
        $humanized = Format-ResultsHumanized -results $searchResults -query $Query
        Write-Host $humanized
    }
    else {
        # Basic output
        Write-Host "`nMarkdown Search Enhanced v$VERSION" -ForegroundColor Cyan
        Write-Host "Query: $Query" -ForegroundColor Yellow
        Write-Host "Path: $Path" -ForegroundColor Gray
        Write-Host ""
        
        if ($searchResults.Count -eq 0) {
            Write-Host "No results found" -ForegroundColor Red
        }
        else {
            Write-Host "Found $($searchResults.Count) result(s) in ${duration}s" -ForegroundColor Green
            Write-Host ""
            
            foreach ($result in $searchResults) {
                Write-Host "$($result.FileName):$($result.LineNumber) (score: $($result.Score))" -ForegroundColor Yellow
                Write-Host "  $($result.Content)" -ForegroundColor White
                Write-Host ""
            }
        }
    }
    
    Write-Host "`nSearch completed in ${duration}s" -ForegroundColor Gray
    if ($byteRoverContext) {
        Write-Host "ByteRover context captured" -ForegroundColor Magenta
    }
}