package com.trading.monitoring.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConsensusVoteDTO {
    
    private String symbol;
    private List<String> agentsInFavor;
    private List<String> agentsAgainst;
    private Double confidenceScore;
    private String finalDecision;
    private String rationale;
}