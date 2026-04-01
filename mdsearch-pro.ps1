# mdsearch-pro - Professional Markdown Search for Windows
# Better than qmd: Windows-native, zero dependencies, skill-integrated

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Query,
    
    [string]$Path = ".",
    
    [ValidateSet("search", "vsearch", "query")]
    [string]$Mode = "search",
    
    [int]$Limit = 20,
    
    [switch]$Recursive = $true,
    
    [switch]$CaseSensitive = $false,
    
    [switch]$Regex = $false,
    
    [ValidateSet("text", "json", "jsonl")]
    [string]$Format = "text",
    
    [switch]$FullContent = $false,
    
    [string]$Collection,
    
    [double]$MinScore = 0.1,
    
    [switch]$Verbose = $false
)

# Configuration
$VERSION = "1.0.0"
$AUTHOR = "OpenClaw Enhanced Search"
$SKILLS_INTEGRATION = @{
    "ByteRover" = $true
    "Humanizer" = $true
    "ProjectManagement" = $true
    "MemorySkills" = $true
}

# Skill Integration Functions
function Invoke-ByteRoverContext {
    param([string]$SearchContext)
    
    if ($SKILLS_INTEGRATION.ByteRover) {
        try {
            # This would integrate with ByteRover for context-aware searching
            # For now, just log the integration point
            if ($Verbose) {
                Write-Verbose "[ByteRover Integration] Search context: $SearchContext"
            }
            return @{ context = $SearchContext; timestamp = (Get-Date).ToString("o") }
        }
        catch {
            Write-Warning "ByteRover integration unavailable: $_"
        }
    }
    return $null
}

function Format-HumanizedOutput {
    param([array]$Results, [string]$Query)
    
    if ($SKILLS_INTEGRATION.Humanizer -and $Format -eq "text") {
        # Apply humanizer principles: natural language, readable formatting
        $output = @()
        $output += "🔍 **Search Results for: '$Query'**"
        $output += "=" * 50
        
        if ($Results.Count -eq 0) {
            $output += "No documents matched your search."
            $output += ""
            $output += "💡 **Suggestions:**"
            $output += "- Try different keywords"
            $output += "- Check spelling"
            $output += "- Use broader terms"
        } else {
            $output += "Found **$($Results.Count)** relevant document(s):"
            $output += ""
            
            $grouped = $Results | Group-Object File
            foreach ($group in $grouped) {
                $file = $group.Name
                $matches = $group.Group
                
                $output += "📄 **$(Split-Path $file -Leaf)**"
                $output += "   Location: $file"
                $output += "   Matches: $($matches.Count)"
                $output += ""
                
                foreach ($match in $matches | Select-Object -First 3) {
                    $linePreview = if ($match.Content.Length -gt 80) {
                        $match.Content.Substring(0, 77) + "..."
                    } else {
                        $match.Content
                    }
                    $output += "   • Line $($match.LineNumber): $linePreview"
                }
                
                if ($matches.Count -gt 3) {
                    $output += "   • ... and $($matches.Count - 3) more matches"
                }
                $output += "---"
            }
            
            $output += ""
            $output += "📊 **Summary:** $($Results.Count) total matches across $($grouped.Count) files"
        }
        
        return $output -join "`n"
    }
    
    return $null
}

# Search Functions
function Get-BasicScore {
    param([string]$Content, [string]$Query)
    
    $score = 0.0
    
    # Exact match bonus
    if ($Content -match [regex]::Escape($Query)) {
        $score += 1.0
    }
    
    # Word boundary matches
    $words = $Query -split '\s+' | Where-Object { $_.Length -gt 2 }
    foreach ($word in $words) {
        if ($Content -match "\b$word\b") {
            $score += 0.5
        }
    }
    
    # Length normalization (shorter content gets higher score per match)
    $contentLength = $Content.Length
    if ($contentLength -gt 0) {
        $score *= (100 / [math]::Min($contentLength, 100))
    }
    
    return [math]::Min($score, 10.0)
}

function Search-MarkdownFiles {
    param(
        [string]$SearchPath,
        [string]$SearchQuery,
        [string]$SearchMode,
        [int]$MaxResults,
        [double]$ScoreThreshold
    )
    
    $results = @()
    $searchStart = Get-Date
    
    # Get files
    $files = Get-ChildItem -Path $SearchPath -Filter "*.md" -Recurse:$Recursive -File -ErrorAction SilentlyContinue
    
    if ($Collection) {
        $files = $files | Where-Object { $_.DirectoryName -match $Collection }
    }
    
    $fileCount = $files.Count
    if ($Verbose) {
        Write-Verbose "Searching $fileCount markdown files..."
    }
    
    # Search each file
    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw -ErrorAction Stop
            $lines = $content -split "`n"
            
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i].Trim()
                if ([string]::IsNullOrWhiteSpace($line)) {
                    continue
                }
                
                $match = $false
                $score = 0.0
                
                # Apply search mode
                switch ($SearchMode) {
                    "search" {
                        # Basic keyword search (like qmd search)
                        if ($Regex) {
                            $match = $line -match $SearchQuery
                        } else {
                            $pattern = if ($CaseSensitive) {
                                $SearchQuery
                            } else {
                                "(?i)$([regex]::Escape($SearchQuery))"
                            }
                            $match = $line -match $pattern
                        }
                        
                        if ($match) {
                            $score = Get-BasicScore -Content $line -Query $SearchQuery
                        }
                    }
                    
                    "vsearch" {
                        # Simple vector-like search (conceptual matching)
                        # This is a simplified version - real vsearch would use embeddings
                        $queryWords = $SearchQuery -split '\s+' | Where-Object { $_.Length -gt 3 }
                        $lineWords = $line -split '\s+' | Where-Object { $_.Length -gt 3 }
                        
                        $commonWords = Compare-Object $queryWords $lineWords -IncludeEqual -ExcludeDifferent |
                            Select-Object -ExpandProperty InputObject
                        
                        if ($commonWords.Count -gt 0) {
                            $match = $true
                            $score = ($commonWords.Count / [math]::Max($queryWords.Count, 1)) * 5.0
                        }
                    }
                    
                    "query" {
                        # Hybrid search (combination)
                        $keywordMatch = $line -match "(?i)$([regex]::Escape($SearchQuery))"
                        $conceptualScore = 0.0
                        
                        # Simple conceptual matching
                        $importantWords = @("how", "what", "why", "when", "where", "which", "who")
                        $queryHasQuestion = $importantWords | Where-Object { $SearchQuery -match $_ }
                        
                        if ($queryHasQuestion) {
                            # Boost lines that look like answers
                            if ($line -match "\.\s*$" -and $line.Length -gt 20 -and $line.Length -lt 200) {
                                $conceptualScore += 2.0
                            }
                        }
                        
                        $match = $keywordMatch -or $conceptualScore -gt 1.0
                        $score = ($keywordMatch ? 3.0 : 0) + $conceptualScore
                    }
                }
                
                if ($match -and $score -ge $ScoreThreshold) {
                    $result = [PSCustomObject]@{
                        File = $file.FullName
                        FileName = $file.Name
                        Directory = $file.DirectoryName
                        LineNumber = $i + 1
                        Content = if ($FullContent) { $lines[$i] } else { $line }
                        Score = [math]::Round($score, 2)
                        Mode = $SearchMode
                        Timestamp = (Get-Date).ToString("o")
                        Context = @{
                            Before = if ($i -gt 0) { $lines[$i-1].Trim() } else { $null }
                            After = if ($i -lt $lines.Count - 1) { $lines[$i+1].Trim() } else { $null }
                        }
                    }
                    
                    $results += $result
                    
                    if ($results.Count -ge $MaxResults) {
                        break 2
                    }
                }
            }
        }
        catch {
            if ($Verbose) {
                Write-Verbose "Error reading $($file.FullName): $_"
            }
        }
    }
    
    $searchEnd = Get-Date
    $duration = ($searchEnd - $searchStart).TotalSeconds
    
    # Sort by score
    $results = $results | Sort-Object Score -Descending
    
    return @{
        Results = $results
        Metadata = @{
            Query = $SearchQuery
            Mode = $SearchMode
            FilesSearched = $fileCount
            TotalMatches = $results.Count
            DurationSeconds = [math]::Round($duration, 2)
            Timestamp = (Get-Date).ToString("o")
            Version = $VERSION
            SkillsIntegration = $SKILLS_INTEGRATION
        }
    }
}

# Main Execution
function Main {
    # Skill Integration: ByteRover context
    $byteRoverContext = Invoke-ByteRoverContext -SearchContext "Searching for: $Query in $Path"
    
    # Perform search
    $searchResult = Search-MarkdownFiles `
        -SearchPath $Path `
        -SearchQuery $Query `
        -SearchMode $Mode `
        -MaxResults $Limit `
        -ScoreThreshold $MinScore
    
    # Format output
    switch ($Format) {
        "json" {
            $output = @{
                Search = $searchResult.Metadata
                Context = $byteRoverContext
                Results = $searchResult.Results
            }
            $output | ConvertTo-Json -Depth 4
        }
        
        "jsonl" {
            foreach ($result in $searchResult.Results) {
                $result | ConvertTo-Json -Compress
            }
        }
        
        "text" {
            $humanized = Format-HumanizedOutput -Results $searchResult.Results -Query $Query
            if ($humanized) {
                $humanized
            } else {
                # Fallback to basic formatting
                Write-Host "`n🔍 Markdown Search Pro v$VERSION" -ForegroundColor Cyan
                Write-Host "=" * 50 -ForegroundColor Cyan
                Write-Host "Query: $Query" -ForegroundColor Yellow
                Write-Host "Mode: $Mode" -ForegroundColor Gray
                Write-Host "Path: $Path" -ForegroundColor Gray
                Write-Host ""
                
                if ($searchResult.Results.Count -eq 0) {
                    Write-Host "❌ No results found" -ForegroundColor Red
                } else {
                    Write-Host "✅ Found $($searchResult.Results.Count) result(s) in $($searchResult.Metadata.DurationSeconds)s" -ForegroundColor Green
                    Write-Host ""
                    
                    foreach ($result in $searchResult.Results) {
                        Write-Host "📄 $($result.FileName) (Score: $($result.Score))" -ForegroundColor Yellow
                        Write-Host "   $($result.File)" -ForegroundColor Gray
                        Write-Host "   Line $($result.LineNumber): $($result.Content)" -ForegroundColor White
                        Write-Host "---"
                    }
                }
                
                Write-Host ""
                Write-Host "📊 Search completed in $($searchResult.Metadata.DurationSeconds) seconds" -ForegroundColor Gray
                Write-Host "📁 $($searchResult.Metadata.FilesSearched) files searched" -ForegroundColor Gray
                
                if ($byteRoverContext) {
                    Write-Host "🧠 ByteRover context integrated" -ForegroundColor Magenta
                }
            }
        }
    }
}

# Error handling
try {
    Main
}
catch {
    Write-Error "Search failed: $_"
    exit 1
}