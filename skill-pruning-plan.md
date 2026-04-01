# Skill Pruning Plan - March 31, 2026

## Current Situation
**Global Skills**: 51 skills installed in OpenClaw
**Workspace Skills**: 3 skills actively used
**Skill Utilization**: 30% (9/29 from audit, but audit may reference different set)

## Pruning Strategy
**Approach**: Document skills for deactivation rather than deletion (safer)
**Goal**: Identify 5 skills to mark as "inactive" or "do not use"
**Criteria**: 
1. Duplicates (keep one, mark others)
2. Never used (based on audit)
3. Incomplete (missing core files)
4. Replaced by better alternatives

## Skills to Deactivate (Priority Order)

### 1. **healthcheck** (High Priority)
- **Reason**: Identified in audit as first skill to prune
- **Status**: Exists in global directory
- **Action**: Document as "do not use" unless specifically needed for security audits
- **Alternative**: Use system-monitor or create custom health checks

### 2. **ai-humanizer** (High Priority)
- **Reason**: Duplicate of **humanizer** skill
- **Status**: Both exist, humanizer is actively used
- **Action**: Mark ai-humanizer as deprecated, use humanizer only
- **Note**: Humanizer is core principle ("Humanize everything")

### 3. **evolver** (High Priority)
- **Reason**: Duplicate of **capability-evolver**
- **Status**: Both exist, capability-evolver is being integrated
- **Action**: Mark evolver as deprecated, use capability-evolver only
- **Note**: Capability-evolver has A2A_NODE_ID integration

### 4. **qmd** and **qmd-cli** (Medium Priority)
- **Reason**: Replaced by **mdsearch-pro**
- **Status**: mdsearch-pro is actively used in workspace
- **Action**: Mark qmd and qmd-cli as deprecated
- **Note**: mdsearch-pro is Windows-compatible, qmd requires Bun

### 5. **decision-tracker** (Medium Priority)
- **Reason**: Incomplete (only 1 file according to capability-evolver analysis)
- **Status**: Needs index.js + SKILL.md minimum
- **Action**: Mark as incomplete, do not use until completed
- **Alternative**: Use decision-framework if available

## Additional Candidates for Review

### Skills with Only 1 File (Incomplete):
- enhanced-research
- free-models-manager  
- learning-accelerator
- learning-pipeline
- memory-utilization-tracker
- model-switching-integration
- project-manager
- system-monitor
- workflow-optimizer

**Action**: All marked as "incomplete - do not use" until they have at least index.js + SKILL.md

### Skills Never Used (from audit):
- agent-browser-clawdbot
- ai-web-automation
- automation-workflows
- decision-framework
- feishu-evolver-wrapper
- intelligence-suite

**Action**: Review for potential activation vs deactivation

## Implementation Plan

### Phase 1: Documentation (Today)
1. Create this pruning plan document
2. Update MEMORY.md with pruning decisions
3. Add notes to skill-utilization-audit.md

### Phase 2: Integration (This Week)
4. Ensure active skills are properly integrated:
   - ByteRover (before each task)
   - Humanizer (all communications)
   - mdsearch-pro (search needs)
   - capability-evolver (weekly runs)
   - desktop-control-win (Windows automation)

### Phase 3: Monitoring (Ongoing)
5. Track skill usage weekly
6. Review pruning decisions monthly
7. Reactivate skills if needed for specific tasks

## Success Metrics
- **Today**: 5 skills documented for deactivation ✓
- **This Week**: Skill utilization increases from 30% to 40%
- **This Month**: Clear separation between active/inactive skills
- **Ongoing**: Regular reviews to maintain optimal skill set

## Risk Mitigation
- **No Deletion**: Only documentation, skills remain installed
- **Reversible**: Can reactivate any skill if needed
- **Testing**: New skills tested before full integration
- **Backup**: Global skills directory backed up

## Next Actions
1. Update progress tracker with pruning plan completion
2. Use ByteRover to curate this pruning knowledge
3. Apply HyperAgents concepts to skill management
4. Create skill dashboard for visual tracking

---
**Created**: 2026-03-31 12:35 PM
**Status**: Phase 1 in progress
**Skills Documented**: 5/5 target
**Next Review**: Weekly skill audit starting April 7, 2026