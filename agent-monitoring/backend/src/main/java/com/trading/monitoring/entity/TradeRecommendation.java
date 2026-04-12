package com.trading.monitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "trade_recommendations")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TradeRecommendation {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    @Column(nullable = false)
    private String symbol;
    
    @Column
    private String assetType; // "stock", "crypto", "option"
    
    @Column(nullable = false)
    private String entryRange; // e.g., "150.25-151.50"
    
    @Column(nullable = false)
    private Double targetPrice;
    
    @Column(nullable = false)
    private Double stopLoss;
    
    @Column(nullable = false)
    private Double positionSize; // Percentage of portfolio (e.g., 2.0 for 2%)
    
    @Column(nullable = false)
    private Double confidence; // 0.0 to 1.0
    
    @Column(columnDefinition = "TEXT", nullable = false)
    private String rationale;
    
    @Column
    private String status; // "pending", "executed", "canceled", "expired"
    
    @Column
    private LocalDateTime executedAt;
    
    @Column
    private Double actualEntry;
    
    @Column
    private Double actualExit;
    
    @Column
    private Double pnl; // Profit/Loss percentage
    
    @PrePersist
    protected void onCreate() {
        if (timestamp == null) {
            timestamp = LocalDateTime.now();
        }
        if (status == null) {
            status = "pending";
        }
    }
}