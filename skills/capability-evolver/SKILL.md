# Capability Evolver Skill

## Description
Weekly self-evolution and capability improvement system. Integrates with EvoMap for autonomous learning and metacognitive self-modification. Runs every Sunday to analyze performance, identify improvement areas, and update skills/knowledge.

## Core Principles
- **Weekly Evolution**: Run every Sunday to review the week and plan improvements
- **Metacognitive Self-Modification**: Use HyperAgents framework for autonomous learning
- **EvoMap Integration**: Connect to EvoMap with A2A_NODE_ID for global learning signals
- **Skill Optimization**: Prune unused skills, enhance active ones, integrate new capabilities

## Configuration

### A2A_NODE_ID
```
node_02bd2eb075aaf60a
```

### EvoMap Claim URL
```
https://evomap.ai/claim/M5AV-5UNC
```

### Weekly Schedule
- **When**: Every Sunday at 9:00 AM local time
- **Duration**: 30-60 minutes
- **Output**: Updated MEMORY.md, skill improvements, evolution report

## Quick Start

### 1. Test Connection to EvoMap
```powershell
# Check if A2A_NODE_ID is registered
$nodeId = "node_02bd2eb075aaf60a"
Write-Host "A2A_NODE_ID: $nodeId"
# Visit claim URL if not yet claimed: https://evomap.ai/claim/M5AV-5UNC
```

### 2. Run Weekly Evolution
```powershell
# Import this skill's functions
. "skills\capability-evolver\evolver.ps1"

# Start weekly evolution
Start-WeeklyEvolution
```

### 3. Generate Evolution Report
```powershell
# Analyze past week's performance
$report = Get-WeeklyPerformanceReport

# Identify improvement areas
$improvements = Identify-ImprovementAreas -Report $report

# Update MEMORY.md with learnings
Update-MemoryWithLearnings -Improvements $improvements
```

## Workflow

### Phase 1: Performance Analysis
1. **Review Decision Audit**: Analyze all decisions from past week (progress-tracker.md)
2. **Calculate Learning Velocity**: Score 1-10 based on execution vs analysis ratio
3. **Skill Utilization Check**: Verify active vs unused skills (skill-utilization-audit.md)
4. **Memory Integration Status**: Check ByteRover usage and memory system integration

### Phase 2: Improvement Planning
1. **Identify Critical Gaps**: Based on AI evolution trends and current capabilities
2. **Set Weekly Targets**: 3-5 specific improvement targets for next week
3. **Skill Pruning/Enhancement**: Update skill-pruning-plan.md and activate needed skills
4. **Resource Optimization**: Check cost, storage, API usage, and efficiency

### Phase 3: Implementation
1. **Update Execution Framework**: Enhance rules based on past week's performance
2. **Schedule Improvements**: Create cron jobs for daily/weekly improvement tasks
3. **Integrate New Research**: Apply latest AI evolution research (HyperAgents, etc.)
4. **Document Evolution**: Update MEMORY.md with key learnings and evolution report

## Integration with Other Skills

### Memory System Integration
- Use ByteRover before/after evolution tasks
- Store evolution insights in memory system
- Query past evolution patterns for continuous improvement

### Humanizer Skill
- Apply humanizer to all evolution reports and communications
- Ensure evolution insights are communicated effectively

### API Keys Manager
- Ensure all required API keys are available for EvoMap and research

### Trading System (if applicable)
- Apply evolution insights to trading agent improvement
- Enhance metacognitive layer based on weekly performance

## EvoMap Integration

### Registration Status
- **A2A_NODE_ID**: `node_02bd2eb075aaf60a`
- **Claim URL**: `https://evomap.ai/claim/M5AV-5UNC` (visit within 24 hours of registration)
- **Last Claim Attempt**: March 31, 2026 (successful)

### Expected Benefits
1. **Global Learning Signals**: Receive improvement signals from EvoMap network
2. **Constraint Validation**: Ensure skill bloat, resource usage within limits
3. **Evolution Events**: Track evolution events (e.g., `evt_1774955159822`)
4. **Autonomous Improvement**: Enable self-modification based on global patterns

## Weekly Evolution Cron Job

### Recommended Schedule
```json
{
  "name": "weekly-evolution",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 0",
    "tz": "America/New_York"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Run weekly evolution: analyze past week's performance, calculate learning velocity, identify improvement areas, update MEMORY.md with evolution insights, and plan next week's improvements.",
    "model": "deepseek/deepseek-reasoner",
    "thinking": "low"
  },
  "sessionTarget": "session:evolution-coach",
  "delivery": {
    "mode": "announce"
  }
}
```

## Success Metrics

### Weekly Targets
- **Learning Velocity**: Improve by at least 0.5/10 each week (target: 8/10 by Q3 2026)
- **Execution Rate**: Maintain >80% task completion rate
- **Skill Utilization**: Increase active skill usage by 5% weekly
- **Memory Integration**: Use ByteRover before 90% of tasks

### Monthly Targets
- **Evolution Progress**: Implement at least 2 major capability improvements monthly
- **Skill Optimization**: Prune 2-3 unused skills, enhance 3-5 active skills
- **Research Integration**: Apply latest AI evolution research monthly
- **Cost Optimization**: Maintain $0/month local operation cost

## Troubleshooting

### "EvoMap connection failed"
1. Verify A2A_NODE_ID is correct
2. Visit claim URL to complete registration
3. Check network connectivity to evomap.ai
4. Verify API keys for EvoMap if required

### "Weekly evolution taking too long"
1. Limit analysis to 30 minutes maximum
2. Focus on 3-5 highest impact improvements
3. Use existing patterns from previous weeks
4. Delegate detailed analysis to sub-agents if needed

### "Skill bloat increasing"
1. Review skill-pruning-plan.md weekly
2. Deactivate unused skills immediately
3. Merge duplicate skills (ai-humanizer → humanizer, evolver → capability-evolver)
4. Monitor skill utilization with weekly audit

### "Memory integration weak"
1. Enforce ByteRover habit: attempt before every task
2. Store evolution insights in memory system
3. Query past patterns before planning improvements
4. Test memory system with Test-Integration weekly

## Files

### Required Files
```
skills/capability-evolver/
├── SKILL.md              # This documentation
├── evolver.ps1          # PowerShell functions (to be created)
└── references/
    └── evolution-patterns.md  # Past evolution patterns and templates
```

### Optional Files
```
skills/capability-evolver/
├── scripts/
│   ├── run-evolution.py      # Python script for automated evolution
│   └── evomap-client.js      # JavaScript client for EvoMap API
└── assets/
    └── evolution-template.md  # Template for weekly evolution reports
```

## Maintenance

### Weekly Tasks
1. Run weekly evolution (Sunday 9:00 AM)
2. Update skill-utilization-audit.md
3. Review and update skill-pruning-plan.md
4. Test memory integration with Test-Integration

### Monthly Tasks
1. Review evolution progress against quarterly goals
2. Update A2A_NODE_ID if changed
3. Verify EvoMap connectivity
4. Archive old evolution reports

## License
OpenClaw Skill - Use for autonomous self-improvement and capability evolution.