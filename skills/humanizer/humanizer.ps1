# Humanizer PowerShell Module
# Apply human touch to communications

# Configuration
$HumanizerRules = @{
    Replacements = @(
        @{ from = "I am capable of assisting you"; to = "I can help with that" },
        @{ from = "The system is operational"; to = "Everything's working smoothly" },
        @{ from = "Please be advised that"; to = "Just so you know" },
        @{ from = "It is recommended that you"; to = "You might want to" },
        @{ from = "Initiate"; to = "Start" },
        @{ from = "Terminate"; to = "Stop" },
        @{ from = "Utilize"; to = "Use" },
        @{ from = "Affirmative"; to = "Yes" },
        @{ from = "Negative"; to = "No" },
        @{ from = "Processing"; to = "Working on" },
        @{ from = "Unable to"; to = "Can't" },
        @{ from = "Please"; to = "" }, # Remove excessive politeness
        @{ from = "Kindly"; to = "" }
    )
    Tone = "friendly" # friendly, professional, concise
    EmojiFrequency = "low" # none, low, medium, high
    UseContractions = $true
}

function Invoke-Humanizer {
    <#
    .SYNOPSIS
    Apply human touch to text
    .PARAMETER Text
    Text to humanize
    .PARAMETER Tone
    Tone profile: friendly, professional, concise
    .PARAMETER EmojiFrequency
    How often to add emoji: none, low, medium, high
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Text,
        
        [Parameter()]
        [ValidateSet("friendly", "professional", "concise")]
        [string]$Tone = "friendly",
        
        [Parameter()]
        [ValidateSet("none", "low", "medium", "high")]
        [string]$EmojiFrequency = "low"
    )
    
    # Apply replacements
    $result = $Text
    foreach ($rule in $HumanizerRules.Replacements) {
        $result = $result -replace $rule.from, $rule.to
    }
    
    # Apply contractions if enabled
    if ($HumanizerRules.UseContractions) {
        $result = $result -replace "I am", "I'm"
        $result = $result -replace "You are", "You're"
        $result = $result -replace "We are", "We're"
        $result = $result -replace "They are", "They're"
        $result = $result -replace "Cannot", "Can't"
        $result = $result -replace "Will not", "Won't"
        $result = $result -replace "Do not", "Don't"
        $result = $result -replace "Does not", "Doesn't"
    }
    
    # Apply tone-specific adjustments
    switch ($Tone) {
        "friendly" {
            # Add friendly phrasing
            if ($result -notmatch "!$") {
                # Add exclamation if doesn't end with punctuation
                $result = $result -replace "\.$", "!"
            }
            # Start with friendly opener occasionally
            $openers = @("Got it!", "Sure thing!", "Alright!", "Okay!")
            if ($result -notmatch "^($($openers -join '|'))") {
                $random = Get-Random -Maximum 4
                if ($random -eq 0) {
                    $opener = $openers | Get-Random
                    $result = "$opener $result"
                }
            }
        }
        "professional" {
            # Keep more formal but still human
            $result = $result -replace "!$", "."
        }
        "concise" {
            # Shorten
            $result = $result -replace "\.\s+", ". "
            # Remove filler words
            $fillers = @("just ", "actually ", "basically ", "literally ")
            foreach ($filler in $fillers) {
                $result = $result -replace $filler, ""
            }
        }
    }
    
    # Add emoji based on frequency
    if ($EmojiFrequency -ne "none") {
        $emojiMap = @{
            "!" = @("😊", "👍", "✨")
            "." = @("😌", "🤔", "📝")
            "?" = @("🤔", "❓", "💭")
        }
        
        $addEmoji = $false
        switch ($EmojiFrequency) {
            "low" { $addEmoji = (Get-Random -Maximum 10) -eq 0 } # 10% chance
            "medium" { $addEmoji = (Get-Random -Maximum 4) -eq 0 } # 25% chance
            "high" { $addEmoji = (Get-Random -Maximum 2) -eq 0 } # 50% chance
        }
        
        if ($addEmoji) {
            $lastChar = $result[-1]
            if ($emojiMap.ContainsKey($lastChar)) {
                $emoji = $emojiMap[$lastChar] | Get-Random
                $result = "$result $emoji"
            }
        }
    }
    
    # Clean up double spaces
    $result = $result -replace "\s+", " "
    
    return $result.Trim()
}

function Test-Humanizer {
    <#
    .SYNOPSIS
    Test humanizer with sample text
    #>
    Write-Host "Testing Humanizer..." -ForegroundColor Cyan
    
    $samples = @(
        "The system is operational. All functions are nominal.",
        "Please be advised that the task has been completed successfully.",
        "I am capable of assisting you with that request.",
        "It is recommended that you optimize your skill utilization.",
        "Processing your request now. Please wait.",
        "Unable to complete the operation due to insufficient resources."
    )
    
    foreach ($sample in $samples) {
        Write-Host "`nBefore: $sample" -ForegroundColor Gray
        $humanized = Invoke-Humanizer -Text $sample
        Write-Host "After:  $humanized" -ForegroundColor Green
    }
    
    Write-Host "`n✅ Humanizer test complete" -ForegroundColor Green
}

function Get-HumanizerStats {
    <#
    .SYNOPSIS
    Get humanizer usage statistics (placeholder)
    #>
    Write-Host "Humanizer Stats" -ForegroundColor Cyan
    Write-Host "---------------" -ForegroundColor Cyan
    Write-Host "Rules loaded: $($HumanizerRules.Replacements.Count)" -ForegroundColor Gray
    Write-Host "Default tone: $($HumanizerRules.Tone)" -ForegroundColor Gray
    Write-Host "Emoji frequency: $($HumanizerRules.EmojiFrequency)" -ForegroundColor Gray
    Write-Host "Use contractions: $($HumanizerRules.UseContractions)" -ForegroundColor Gray
    Write-Host "`nNote: Actual usage tracking would require integration with messaging system." -ForegroundColor Yellow
}

function Set-HumanizerConfig {
    <#
    .SYNOPSIS
    Update humanizer configuration
    #>
    param(
        [Parameter()]
        [ValidateSet("friendly", "professional", "concise")]
        [string]$Tone,
        
        [Parameter()]
        [ValidateSet("none", "low", "medium", "high")]
        [string]$EmojiFrequency,
        
        [Parameter()]
        [bool]$UseContractions
    )
    
    if ($Tone) { $HumanizerRules.Tone = $Tone }
    if ($EmojiFrequency) { $HumanizerRules.EmojiFrequency = $EmojiFrequency }
    if ($PSBoundParameters.ContainsKey('UseContractions')) { $HumanizerRules.UseContractions = $UseContractions }
    
    Write-Host "✅ Humanizer configuration updated" -ForegroundColor Green
    Get-HumanizerStats
}

# Export functions
Export-ModuleMember -Function Invoke-Humanizer, Test-Humanizer, Get-HumanizerStats, Set-HumanizerConfig

Write-Host "Humanizer module loaded. Use Invoke-Humanizer to humanize text." -ForegroundColor Cyan