package com.roadsense.backend.client;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.roadsense.backend.exception.ServiceUnavailableException;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
public class RagServiceClient {

    private static final Logger logger = LoggerFactory.getLogger(RagServiceClient.class);

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
        int maxAttempts = 4;
        Exception lastException = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return restClient.post()
                        .uri(ragServiceUrl + "/api/v1/road-assessment")
                        .header(HttpHeaders.USER_AGENT, "RoadSense-Backend/1.0 (Spring-Boot/3.2.5; Java/21)")
                        .contentType(MediaType.APPLICATION_JSON)
                        .body(request)
                        .retrieve()
                        .body(RagResponseDTO.class);

            } catch (RestClientResponseException e) {
                lastException = e;
                int statusCode = e.getStatusCode().value();
                logger.warn("RAG service attempt {}/{} failed with HTTP {}", attempt, maxAttempts, statusCode);

                if ((statusCode == 502 || statusCode == 503 || statusCode == 504) && attempt < maxAttempts) {
                    try {
                        Thread.sleep(3000);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                    continue;
                }
                break;

            } catch (Exception e) {
                lastException = e;
                logger.warn("RAG service attempt {}/{} failed: [{}] {}", attempt, maxAttempts, e.getClass().getName(), e.getMessage());
                if (attempt < maxAttempts) {
                    try {
                        Thread.sleep(3000);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                    continue;
                }
                break;
            }
        }

        if (lastException instanceof RestClientResponseException rcre) {
            int code = rcre.getStatusCode().value();
            throw new ServiceUnavailableException(
                    "Evidence-Aware Adaptive RAG Service is currently waking up or unavailable (HTTP " + code + "). Please wait 10 seconds and try again."
            );
        }

        throw new ServiceUnavailableException(
                "Evidence-Aware Adaptive RAG Service is currently unavailable: " + (lastException != null ? lastException.getMessage() : "Connection timeout")
        );
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
