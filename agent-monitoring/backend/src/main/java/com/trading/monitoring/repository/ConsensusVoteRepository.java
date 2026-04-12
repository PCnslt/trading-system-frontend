package com.trading.monitoring.repository;

import com.trading.monitoring.entity.ConsensusVote;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ConsensusVoteRepository extends JpaRepository<ConsensusVote, Long> {
    
    List<ConsensusVote> findBySymbolOrderByTimestampDesc(String symbol);
    
    List<ConsensusVote> findByFinalDecisionOrderByTimestampDesc(String finalDecision);
    
    @Query("SELECT c FROM ConsensusVote c WHERE c.timestamp >= :start AND c.timestamp <= :end ORDER BY c.timestamp DESC")
    List<ConsensusVote> findVotesInTimeRange(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
    
    @Query("SELECT c FROM ConsensusVote c ORDER BY c.timestamp DESC LIMIT :limit")
    List<ConsensusVote> findRecentVotes(@Param("limit") int limit);
    
    @Query("SELECT DISTINCT c.symbol FROM ConsensusVote c")
    List<String> findDistinctSymbols();
}