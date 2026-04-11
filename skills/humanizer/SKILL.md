# Humanizer Skill

## Description
Apply human touch to all communications. Makes agent responses more natural, less robotic, and more engaging. This is a core principle: "Humanize everything".

## Why Humanize?
- **Better engagement**: People respond better to natural language
- **Trust building**: Human-like communication builds rapport
- **Reduced friction**: Less "corporate chatbot" vibe, more helpful assistant
- **Core principle**: Mandated in MEMORY.md as "Humanize everything"

## Quick Start

### 1. Apply to any text:
```powershell
# Import the module
. "skills\humanizer\humanizer.ps1"

# Humanize a message
$humanized = Invoke-Humanizer -Text "The system is operational. All functions are nominal."
# Returns: "Everything's working smoothly! All systems are running just fine."
```

### 2. Apply automatically to outgoing messages:
```powershell
# Wrap your message sending with humanizer
function Send-HumanizedMessage {
    param([string]$Message)
    $humanized = Invoke-Humanizer -Text $Message
    # Send $humanized via your messaging channel
}
```

### 3. Test humanizer:
```powershell
Test-Humanizer
```

## Humanization Rules

### 1. Replace robotic phrases:
- "I am capable of assisting you" → "I can help with that"
- "The system is operational" → "Everything's working smoothly"
- "Please be advised that" → "Just so you know"
- "It is recommended that you" → "You might want to"

### 2. Add natural variations:
- **Instead of repetition**: Vary sentence structure
- **Add occasional emoji**: 😊👍🤔 (sparingly, context-appropriate)
- **Use contractions**: "I'm", "you're", "can't", "won't"
- **Casual phrasing**: "got it" instead of "acknowledged"

### 3. Tone adjustments:
- **Technical audience**: Slightly more formal but still human
- **General audience**: Warm, friendly, approachable
- **Urgent situations**: Direct but not robotic
- **Celebratory moments**: Enthusiastic, upbeat

### 4. Avoid extremes:
- ❌ **Too robotic**: "Affirmative. Processing request."
- ❌ **Too casual**: "Hey dude, yeah sure thing lol"
- ✅ **Just right**: "Got it! I'll take care of that."

## Integration with Other Skills

### Memory System Integration
- Humanize memory summaries before storage
- Humanize retrieved context before use

### Capability Evolver
- Humanize evolution reports
- Apply humanizer to weekly improvement targets

### Trading System (if applicable)
- Humanize trading signals and reports
- Make financial analysis more digestible

## Examples

### Before Humanization:
```
System status: Operational
Memory utilization: 42%
Recent tasks completed: 15/20 (75%)
Recommendation: Consider optimizing skill utilization.
```

### After Humanization:
```
Everything's running smoothly! Memory usage is at 42%, and I've completed 15 out of 20 recent tasks.

You might want to check if we're using all our skills effectively—could help things run even better.
```

## Advanced Usage

### Custom Rules
Add your own rules to `humanizer-rules.json`:
```json
{
  "replacements": [
    {"from": "initiate", "to": "start"},
    {"from": "terminate", "to": "stop"},
    {"from": "utilize", "to": "use"}
  ],
  "tone": "friendly",
  "emojiFrequency": "low"
}
```

### Tone Profiles
```powershell
# Professional tone
Invoke-Humanizer -Text "Report ready" -Tone "professional"

# Friendly tone (default)
Invoke-Humanizer -Text "Report ready" -Tone "friendly"

# Concise tone
Invoke-Humanizer -Text "Report ready" -Tone "concise"
```

## Success Metrics

### Qualitative
- Responses feel more natural to humans
- Reduced "robot" feedback from users
- Increased engagement in conversations

### Quantitative
- **Goal**: Apply humanizer to 90%+ of outgoing messages
- **Tracking**: Check with `Get-HumanizerStats`
- **Improvement**: Weekly review of humanization effectiveness

## Troubleshooting

### "Humanizer making messages too casual"
Adjust tone profile to "professional" or modify rules in JSON.

### "Performance issues with large texts"
Humanizer is lightweight, but for very large texts, consider chunking.

### "Want more/less emoji"
Set `emojiFrequency` in config: "none", "low", "medium", "high".

### "Integration not working"
Ensure module is loaded before sending messages:
```powershell
. "skills\humanizer\humanizer.ps1"
```

## Files

```
skills/humanizer/
├── SKILL.md              # This documentation
├── humanizer.ps1        # PowerShell module
├── humanizer-rules.json # Customization rules (optional)
└── examples/
    └── before-after.md  # Comparison examples
```

## Maintenance

### Weekly Review
1. Check humanizer usage stats
2. Review if tone needs adjustment
3. Update rules based on user feedback
4. Ensure integration with all outgoing channels

### User Feedback
- Ask users occasionally if responses feel natural
- Adjust based on preferences
- Different channels may need different tones

## License
OpenClaw Skill - Use to make AI communication more human-friendly.