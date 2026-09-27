package com.roadsense.backend.controller;

import com.roadsense.backend.service.ChatService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping
    public ResponseEntity<ChatService.ChatResponse> askRoadSense(
            Authentication authentication,
            @RequestBody ChatService.ChatRequest request
    ) {
        String userId = (String) authentication.getPrincipal();
        ChatService.ChatResponse response = chatService.askRoadSense(userId, request);
        return ResponseEntity.ok(response);
    }
}
