package com.trading.monitoring.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TradeRecommendationDTO {
    
    private String symbol;
    private String assetType;
    private String entryRange;
    private Double targetPrice;
    private Double stopLoss;
    private Double positionSize;
    private Double confidence;
    private String rationale;
}