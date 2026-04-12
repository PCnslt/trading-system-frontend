package com.trading.monitoring.controller;

import com.trading.monitoring.dto.AgentActivityDTO;
import com.trading.monitoring.entity.AgentActivity;
import com.trading.monitoring.repository.AgentActivityRepository;
import com.trading.monitoring.service.WebSocketService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/activities")
@RequiredArgsConstructor
public class AgentActivityController {
    
    private final AgentActivityRepository activityRepository;
    private final WebSocketService webSocketService;
    private final ObjectMapper objectMapper;
    
    @PostMapping
    public ResponseEntity<AgentActivity> logActivity(@Valid @RequestBody AgentActivityDTO dto) throws JsonProcessingException {
        AgentActivity activity = new AgentActivity();
        activity.setAgentId(dto.getAgentId());
        activity.setAgentName(dto.getAgentName());
        activity.setTimestamp(LocalDateTime.now());
        activity.setTaskName(dto.getTaskName());
        activity.setActivityType(dto.getActivityType());
        activity.setInputData(dto.getInputData() != null ? objectMapper.writeValueAsString(dto.getInputData()) : null);
        activity.setOutputData(dto.getOutputData() != null ? objectMapper.writeValueAsString(dto.getOutputData()) : null);
        activity.setReasoning(dto.getReasoning());
        activity.setStatus(dto.getStatus() != null ? dto.getStatus() : "completed");
        activity.setDurationMs(dto.getDurationMs());
        activity.setConfidenceScore(dto.getConfidenceScore());
        
        AgentActivity saved = activityRepository.save(activity);
        
        // Broadcast via WebSocket
        webSocketService.broadcastActivity(dto);
        
        return ResponseEntity.ok(saved);
    }
    
    @GetMapping
    public ResponseEntity<List<AgentActivity>> getAllActivities(
            @RequestParam(required = false) String agentId,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String activityType,
            @RequestParam(defaultValue = "100") int limit) {
        
        List<AgentActivity> activities;
        if (agentId != null) {
            activities = activityRepository.findByAgentIdOrderByTimestampDesc(agentId);
        } else if (status != null) {
            activities = activityRepository.findByStatusOrderByTimestampDesc(status);
        } else if (activityType != null) {
            activities = activityRepository.findByActivityTypeOrderByTimestampDesc(activityType);
        } else {
            activities = activityRepository.findRecentActivities(limit);
        }
        
        return ResponseEntity.ok(activities);
    }
    
    @GetMapping("/agents")
    public ResponseEntity<List<String>> getDistinctAgents() {
        return ResponseEntity.ok(activityRepository.findDistinctAgentIds());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<AgentActivity> getActivityById(@PathVariable Long id) {
        return activityRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}