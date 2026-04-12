package com.trading.monitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "agent_activities")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentActivity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String agentId; // e.g., "technical-analyst", "sentiment-analyst"
    
    @Column(nullable = false)
    private String agentName; // Human-readable name
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    @Column(nullable = false)
    private String taskName; // e.g., "pre-market-scan", "sentiment-analysis"
    
    @Column(nullable = false)
    private String activityType; // "scan", "calculate", "analyze", "decision", "error"
    
    @Column(columnDefinition = "TEXT")
    private String inputData; // JSON string of inputs
    
    @Column(columnDefinition = "TEXT")
    private String outputData; // JSON string of outputs
    
    @Column(columnDefinition = "TEXT")
    private String reasoning; // Agent's internal reasoning
    
    @Column(nullable = false)
    private String status; // "in_progress", "completed", "failed"
    
    @Column
    private Integer durationMs; // How long the task took
    
    @Column
    private Double confidenceScore; // 0.0 to 1.0
    
    @PrePersist
    protected void onCreate() {
        if (timestamp == null) {
            timestamp = LocalDateTime.now();
        }
    }
}