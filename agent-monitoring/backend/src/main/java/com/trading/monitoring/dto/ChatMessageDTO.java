package com.trading.monitoring.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessageDTO {
    
    private String senderAgentId;
    private String receiverAgentId; // null for broadcast
    private String message;
    private String context;
    private String messageType;
    private Boolean isUserMessage = false;
}