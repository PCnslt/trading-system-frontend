package com.trading.monitoring.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "chat_messages")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessage {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String senderAgentId;
    
    @Column
    private String receiverAgentId; // null for broadcast or user messages
    
    @Column(nullable = false)
    private LocalDateTime timestamp;
    
    @Column(columnDefinition = "TEXT", nullable = false)
    private String message;
    
    @Column
    private String context; // e.g., "consensus-discussion", "error-resolution"
    
    @Column
    private String messageType; // "info", "question", "alert", "decision"
    
    @Column
    private Boolean isUserMessage = false;
    
    @PrePersist
    protected void onCreate() {
        if (timestamp == null) {
            timestamp = LocalDateTime.now();
        }
    }
}