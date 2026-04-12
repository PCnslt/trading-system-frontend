package com.trading.monitoring.repository;

import com.trading.monitoring.entity.TradeRecommendation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface TradeRecommendationRepository extends JpaRepository<TradeRecommendation, Long> {
    
    List<TradeRecommendation> findBySymbolOrderByTimestampDesc(String symbol);
    
    List<TradeRecommendation> findByStatusOrderByTimestampDesc(String status);
    
    List<TradeRecommendation> findByAssetTypeOrderByTimestampDesc(String assetType);
    
    @Query("SELECT t FROM TradeRecommendation t WHERE t.timestamp >= :start AND t.timestamp <= :end ORDER BY t.timestamp DESC")
    List<TradeRecommendation> findRecommendationsInTimeRange(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
    
    @Query("SELECT t FROM TradeRecommendation t WHERE t.confidence >= :minConfidence ORDER BY t.timestamp DESC")
    List<TradeRecommendation> findByMinConfidence(@Param("minConfidence") double minConfidence);
    
    @Query("SELECT t FROM TradeRecommendation t ORDER BY t.timestamp DESC LIMIT :limit")
    List<TradeRecommendation> findRecentRecommendations(@Param("limit") int limit);
    
    @Query("SELECT t FROM TradeRecommendation t WHERE t.pnl IS NOT NULL ORDER BY t.timestamp DESC")
    List<TradeRecommendation> findExecutedTradesWithPnl();
}