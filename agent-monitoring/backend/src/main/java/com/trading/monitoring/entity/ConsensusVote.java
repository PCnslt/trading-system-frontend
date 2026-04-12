package com.trading.monitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "consensus_votes")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConsensusVote {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    @Column(nullable = false)
    private String symbol; // e.g., "AAPL", "BTC"
    
    @ElementCollection
    @CollectionTable(name = "consensus_agents_in_favor", joinColumns = @JoinColumn(name = "consensus_vote_id"))
    @Column(name = "agent_id")
    private List<String> agentsInFavor;
    
    @ElementCollection
    @CollectionTable(name = "consensus_agents_against", joinColumns = @JoinColumn(name = "consensus_vote_id"))
    @Column(name = "agent_id")
    private List<String> agentsAgainst;
    
    @Column(nullable = false)
    private Double confidenceScore; // 0.0 to 1.0
    
    @Column(nullable = false)
    private String finalDecision; // "BUY", "SELL", "HOLD", "NO_TRADE"
    
    @Column(columnDefinition = "TEXT")
    private String rationale; // Summary of reasoning
    
    @Column
    private Integer totalAgents; // Total agents participated
    
    @PrePersist
    protected void onCreate() {
        if (timestamp == null) {
            timestamp = LocalDateTime.now();
        }
        if (totalAgents == null) {
            totalAgents = (agentsInFavor != null ? agentsInFavor.size() : 0) + 
                          (agentsAgainst != null ? agentsAgainst.size() : 0);
        }
    }
}