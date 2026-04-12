package com.trading.monitoring.controller;

import com.trading.monitoring.dto.ChatMessageDTO;
import com.trading.monitoring.entity.ChatMessage;
import com.trading.monitoring.repository.ChatMessageRepository;
import com.trading.monitoring.service.WebSocketService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatMessageController {
    
    private final ChatMessageRepository chatRepository;
    private final WebSocketService webSocketService;
    
    @PostMapping
    public ResponseEntity<ChatMessage> sendMessage(@Valid @RequestBody ChatMessageDTO dto) {
        ChatMessage message = new ChatMessage();
        message.setSenderAgentId(dto.getSenderAgentId());
        message.setReceiverAgentId(dto.getReceiverAgentId());
        message.setTimestamp(LocalDateTime.now());
        message.setMessage(dto.getMessage());
        message.setContext(dto.getContext());
        message.setMessageType(dto.getMessageType());
        message.setIsUserMessage(dto.getIsUserMessage() != null ? dto.getIsUserMessage() : false);
        
        ChatMessage saved = chatRepository.save(message);
        
        // Broadcast via WebSocket
        webSocketService.broadcastChat(dto);
        
        return ResponseEntity.ok(saved);
    }
    
    @GetMapping
    public ResponseEntity<List<ChatMessage>> getMessages(
            @RequestParam(required = false) String sender,
            @RequestParam(required = false) String receiver,
            @RequestParam(required = false) Boolean isUser,
            @RequestParam(defaultValue = "100") int limit) {
        
        List<ChatMessage> messages;
        if (sender != null) {
            messages = chatRepository.findBySenderAgentIdOrderByTimestampDesc(sender);
        } else if (receiver != null) {
            messages = chatRepository.findByReceiverAgentIdOrderByTimestampDesc(receiver);
        } else if (isUser != null) {
            messages = chatRepository.findByUserMessage(isUser);
        } else {
            messages = chatRepository.findRecentMessages(limit