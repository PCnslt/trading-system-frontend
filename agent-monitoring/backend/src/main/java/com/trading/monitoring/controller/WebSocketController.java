package com.trading.monitoring.controller;

import com.trading.monitoring.dto.AgentActivityDTO;
import com.trading.monitoring.dto.ChatMessageDTO;
import com.trading.monitoring.dto.ConsensusVoteDTO;
import com.trading.monitoring.dto.TradeRecommendationDTO;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

@Controller
public class WebSocketController {
    
    @MessageMapping("/activity")
    @SendTo("/topic/activities")
    public AgentActivityDTO sendActivity(AgentActivityDTO activity) {
        return activity;
    }
    
    @MessageMapping("/chat")
    @SendTo("/topic/chat")
    public ChatMessageDTO sendChat(ChatMessageDTO chat) {
        return chat;
    }
    
    @MessageMapping("/consensus")
    @SendTo("/topic/consensus")
    public ConsensusVoteDTO sendConsensus(ConsensusVoteDTO consensus) {
        return consensus;
    }
    
    @MessageMapping("/trade")
    @SendTo("/topic/trades")
    public TradeRecommendationDTO sendTrade(TradeRecommendationDTO trade) {
        return trade;
    }
}