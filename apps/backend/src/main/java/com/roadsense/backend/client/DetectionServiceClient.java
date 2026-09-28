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
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import java.util.ArrayList;
import java.util.List;

@Component
public class DetectionServiceClient {

    private static final Logger logger = LoggerFactory.getLogger(DetectionServiceClient.class);

    private final RestClient restClient;
    private final String detectionServiceUrl;

    public DetectionServiceClient(
            RestClient restClient,
            @Value("${services.detection-service.url}") String detectionServiceUrl
    ) {
        this.restClient = restClient;
        this.detectionServiceUrl = detectionServiceUrl;
    }

    public DetectionResponseDTO detectDamage(byte[] imageBytes, String filename, double threshold) {
        MediaType mediaType = MediaType.IMAGE_JPEG;
        if (filename != null) {
            String lower = filename.toLowerCase();
            if (lower.endsWith(".png")) {
                mediaType = MediaType.IMAGE_PNG;
            } else if (lower.endsWith(".gif")) {
                mediaType = MediaType.IMAGE_GIF;
            } else if (lower.endsWith(".webp")) {
                mediaType = MediaType.parseMediaType("image/webp");
            }
        }

        String actualFilename = (filename != null && !filename.isBlank()) ? filename : "image.jpg";

        int maxAttempts = 4;
        Exception lastException = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                MultipartBodyBuilder bodyBuilder = new MultipartBodyBuilder();
                bodyBuilder.part("file", new ByteArrayResource(imageBytes) {
                    @Override
                    public String getFilename() {
                        return actualFilename;
                    }
                }, mediaType);

                return restClient.post()
                        .uri(detectionServiceUrl + "/predict?threshold=" + threshold)
                        .header(HttpHeaders.USER_AGENT, "RoadSense-Backend/1.0 (Spring-Boot/3.2.5; Java/21)")
                        .body(bodyBuilder.build())
                        .retrieve()
                        .body(DetectionResponseDTO.class);

            } catch (RestClientResponseException e) {
                lastException = e;
                int statusCode = e.getStatusCode().value();
                logger.warn("Detection service attempt {}/{} failed with HTTP {}", attempt, maxAttempts, statusCode);

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
                logger.warn("Detection service attempt {}/{} failed: [{}] {}", attempt, maxAttempts, e.getClass().getName(), e.getMessage());
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
                    "RF-DETR Detection Service is currently waking up or unavailable (HTTP " + code + "). Please wait 10 seconds and try submitting again."
            );
        }

        throw new ServiceUnavailableException(
                "RF-DETR Detection Service is currently unavailable: " + (lastException != null ? lastException.getMessage() : "Connection timeout")
        );
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DetectionResponseDTO {
        @Builder.Default
        private List<DetectionItemDTO> detections = new ArrayList<>();

        @JsonProperty("damage_type")
        private String damageType;

        private Double confidence;

        @JsonProperty("bounding_box")
        private List<Double> boundingBox;

        @JsonProperty("detection_count")
        private int detectionCount;

        @JsonProperty("image_width")
        private int imageWidth;

        @JsonProperty("image_height")
        private int imageHeight;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DetectionItemDTO {
        @JsonProperty("damage_type")
        private String damageType;

        private double confidence;

        @JsonProperty("bounding_box")
        private List<Double> boundingBox;

        @JsonProperty("class_id")
        private int classId;
    }
}
