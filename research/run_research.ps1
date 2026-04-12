function Invoke-Ollama {
    param([string]$prompt, [string]$model = "llama3.2:3b")
    $clean = $prompt | ollama run $model 2>&1
    # Remove ANSI escape sequences
    $clean -replace '\x1b\[[0-9;]*[a-zA-Z]', ''
}

$outputDir = ".\research\output"
New-Item -ItemType Directory -Force -Path $outputDir

Write-Host "Task 1: Long-term AI trends"
$prompt1 = Get-Content -Raw ".\ai_trends_prompt.txt"
$result1 = Invoke-Ollama -prompt $prompt1
$result1 | Out-File -FilePath "$outputDir\ai_trends.md" -Encoding utf8
Write-Host "Saved."

Write-Host "Task 2: Skill gaps"
$prompt2 = @"
Analyze skill gaps for an AI agent system with 30 installed skills but only 23% utilization.
Consider: execution engine gaps, progress tracking, autonomous agents, AGI preparation, regulatory compliance.
Provide specific gap analysis and prioritize improvements.
Current context: We have skills like ByteRover, qmd, capability-evolver, humanizer, memory systems.
Output in structured markdown.
"@
$result2 = Invoke-Ollama -prompt $prompt2
$result2 | Out-File -FilePath "$outputDir\skill_gaps.md" -Encoding utf8
Write-Host "Saved."

Write-Host "Task 3: Resource optimization"
$prompt3 = @"
Plan resource optimization for AI agent system with 96% cache hit on free local models.
Consider: cost optimization (<$50/month), skill pruning, model selection, infrastructure efficiency.
Provide actionable optimization strategies with metrics.
Current context: Using Ollama models (llama3.2:3b, qwen2.5:32b), PostgreSQL vector memory, Docker.
Output in structured markdown.
"@
$result3 = Invoke-Ollama -prompt $prompt3
$result3 | Out-File -FilePath "$outputDir\resource_optimization.md" -Encoding utf8
Write-Host "Saved."

Write-Host "Task 4: Improvement roadmap"
$prompt4 = @"
Create a 5-month improvement roadmap (April-August 2026) for AI agent system.
Phases: Execution foundation, skill integration, AGI readiness, regulatory compliance.
Include success metrics: execution success 80%, skill utilization 60%, memory efficiency 10x.
Provide quarterly milestones and monthly deliverables.
Current context: Current learning velocity 4/10, target 8/10.
Output in structured markdown.
"@
$result4 = Invoke-Ollama -prompt $prompt4
$result4 | Out-File -FilePath "$outputDir\improvement_roadmap.md" -Encoding utf8
Write-Host "Saved."

Write-Host "All tasks completed."