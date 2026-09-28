package com.roadsense.backend.client;

import com.fasterxml.jackson.annotation.JsonProperty;
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
        @JsonProperty("road_context")
        private Map<String, Object> roadContext;
        private Map<String, Object> weather;
        private Map<String, Object> traffic;
        @JsonProperty("detector_results")
        private Map<String, Object> detectorResults;
        @JsonProperty("rag_mode")
        private String ragMode;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RagResponseDTO {
        @JsonProperty("assessment_id")
        private String assessmentId;
        private String query;
        @JsonProperty("rag_mode")
        private String ragMode;
        @JsonProperty("latency_ms")
        private double latencyMs;
        @Builder.Default
        private List<Map<String, Object>> damage = new ArrayList<>();
        @JsonProperty("location_context")
        private Map<String, Object> locationContext;
        @JsonProperty("weather_context")
        private Map<String, Object> weatherContext;
        @JsonProperty("traffic_context")
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
