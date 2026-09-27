package com.roadsense.backend.client;

import com.roadsense.backend.exception.ServiceUnavailableException;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
public class RagServiceClient {

    private final RestClient restClient;
    private final String ragServiceUrl;

    public RagServiceClient(
            RestClient restClient,
            @Value("${services.rag-service.url}") String ragServiceUrl
    ) {
        this.restClient = restClient;
        this.ragServiceUrl = ragServiceUrl;
    }

    public RagResponseDTO generateAssessmentReport(RagRequestDTO request) {
        try {
            return restClient.post()
                    .uri(ragServiceUrl + "/api/v1/road-assessment")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(RagResponseDTO.class);
        } catch (Exception e) {
            throw new ServiceUnavailableException("Evidence-Aware Adaptive RAG Service is currently unavailable: " + e.getMessage());
        }
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RagRequestDTO {
        private String query;
        private Double latitude;
        private Double longitude;
        private Map<String, Object> roadContext;
        private Map<String, Object> weather;
        private Map<String, Object> traffic;
        private Map<String, Object> detectorResults;
        private String ragMode;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RagResponseDTO {
        private String assessmentId;
        private String query;
        private String ragMode;
        private double latencyMs;
        @Builder.Default
        private List<Map<String, Object>> damage = new ArrayList<>();
        private Map<String, Object> locationContext;
        private Map<String, Object> weatherContext;
        private Map<String, Object> trafficContext;
        @Builder.Default
        private List<Map<String, Object>> evidence = new ArrayList<>();
        private Map<String, Object> verification;
        private String report;
        @Builder.Default
        private List<String> uncertainties = new ArrayList<>();
        @Builder.Default
        private List<Map<String, Object>> sources = new ArrayList<>();
    }
}
