package com.roadsense.backend.service;

import com.roadsense.backend.client.RagServiceClient;
import com.roadsense.backend.exception.ResourceNotFoundException;
import com.roadsense.backend.model.Assessment;
import com.roadsense.backend.repository.AssessmentRepository;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class ChatService {

    private final AssessmentRepository assessmentRepository;
    private final RagServiceClient ragClient;

    public ChatService(AssessmentRepository assessmentRepository, RagServiceClient ragClient) {
        this.assessmentRepository = assessmentRepository;
        this.ragClient = ragClient;
    }

    public ChatResponse askRoadSense(String userId, ChatRequest request) {
        Map<String, Object> detectorInput = Map.of();
        Map<String, Object> locationInput = Map.of();

        if (request.getAssessmentId() != null && !request.getAssessmentId().isBlank()) {
            Optional<Assessment> assessmentOpt = assessmentRepository.findByAssessmentIdAndUserId(request.getAssessmentId(), userId);
            if (assessmentOpt.isPresent()) {
                Assessment ass = assessmentOpt.get();
                if (ass.getLocation() != null) {
                    locationInput = Map.of(
                            "mapped_road", ass.getLocation().getRoad() != null ? ass.getLocation().getRoad() : "Road Corridor",
                            "road_type", ass.getLocation().getRoadType() != null ? ass.getLocation().getRoadType() : "National Highway"
                    );
                }
            }
        }

        String mode = (request.getRagMode() != null && !request.getRagMode().isBlank())
                ? request.getRagMode()
                : "EVIDENCE_AWARE_ADAPTIVE_RAG";

        RagServiceClient.RagRequestDTO ragReq = RagServiceClient.RagRequestDTO.builder()
                .query(request.getQuestion())
                .roadContext(locationInput)
                .weather(Map.of("rainfall_mm", 20.0))
                .traffic(Map.of("volume_level", "High"))
                .detectorResults(detectorInput)
                .ragMode(mode)
                .build();

        RagServiceClient.RagResponseDTO ragResp = ragClient.generateAssessmentReport(ragReq);

        List<Map<String, Object>> citations = ragResp.getSources() != null ? ragResp.getSources() : List.of();

        return ChatResponse.builder()
                .question(request.getQuestion())
                .answer(ragResp.getReport())
                .citations(citations)
                .ragMode(ragResp.getRagMode())
                .latencyMs(ragResp.getLatencyMs())
                .build();
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ChatRequest {
        private String question;
        private String assessmentId;
        private String ragMode;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ChatResponse {
        private String question;
        private String answer;
        @Builder.Default
        private List<Map<String, Object>> citations = new ArrayList<>();
        private String ragMode;
        private double latencyMs;
    }
}
