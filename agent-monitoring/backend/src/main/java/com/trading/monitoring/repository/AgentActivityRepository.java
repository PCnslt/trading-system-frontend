package com.trading.monitoring.repository;

import com.trading.monitoring.entity.AgentActivity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AgentActivityRepository extends JpaRepository<AgentActivity, Long> {
    
    List<AgentActivity> findByAgentIdOrderByTimestampDesc(String agentId);
    
    List<AgentActivity> findByStatusOrderByTimestampDesc(String status);
    
    List<AgentActivity> findByActivityTypeOrderByTimestampDesc(String activityType);
    
    @Query("SELECT a FROM AgentActivity a WHERE a.timestamp >= :start AND a.timestamp <= :end ORDER BY a.timestamp DESC")
    List<AgentActivity> findActivitiesInTimeRange(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
    
    @Query("SELECT a FROM AgentActivity a WHERE a.agentId = :agentId AND a.timestamp >= :start AND a.timestamp <= :end ORDER BY a.timestamp DESC")
    List<AgentActivity> findAgentActivitiesInTimeRange(@Param("agentId") String agentId, 
                                                      @Param("start") LocalDateTime start, 
                                                      @Param("end") LocalDateTime end);
    
    @Query("SELECT DISTINCT a.agentId FROM AgentActivity a")
    List<String> findDistinctAgentIds();
    
    @Query("SELECT a FROM AgentActivity a ORDER BY a.timestamp DESC LIMIT :limit")
    List<AgentActivity> findRecentActivities(@Param("limit") int limit);
}