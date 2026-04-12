package com.trading.monitoring.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentActivityDTO {
    
    private String agentId;
    private String agentName;
    private String taskName;
    private String activityType;
    private Map<String, Object> inputData;
    private Map<String, Object> outputData;
    private String reasoning;
    private String status;
    private Integer durationMs;
    private Double confidenceScore;
    
    // Helper method to set timestamp on entity
    public LocalDateTime getTimestamp() {
        return LocalDateTime.now();
    }
}