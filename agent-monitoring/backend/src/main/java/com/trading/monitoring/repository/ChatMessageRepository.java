package com.trading.monitoring.repository;

import com.trading.monitoring.entity.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {
    
    List<ChatMessage> findBySenderAgentIdOrderByTimestampDesc(String senderAgentId);
    
    List<ChatMessage> findByReceiverAgentIdOrderByTimestampDesc(String receiverAgentId);
    
    @Query("SELECT c FROM ChatMessage c WHERE (c.senderAgentId = :agentId OR c.receiverAgentId = :agentId) ORDER BY c.timestamp DESC")
    List<ChatMessage> findMessagesInvolvingAgent(@Param("agentId") String agentId);
    
    @Query("SELECT c FROM ChatMessage c WHERE c.timestamp >= :start AND c.timestamp <= :end ORDER BY c.timestamp DESC")
    List<ChatMessage> findMessagesInTimeRange(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
    
    @Query("SELECT c FROM ChatMessage c ORDER BY c.timestamp DESC LIMIT :limit")
    List<ChatMessage> findRecentMessages(@Param("limit") int limit);
    
    @Query("SELECT c FROM ChatMessage c WHERE c.isUserMessage = :isUser ORDER BY c.timestamp DESC")
    List<ChatMessage> findByUserMessage(@Param("isUser") boolean isUser);
}