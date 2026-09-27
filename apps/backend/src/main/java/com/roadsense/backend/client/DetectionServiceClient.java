package com.roadsense.backend.client;

import com.roadsense.backend.exception.ServiceUnavailableException;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.ArrayList;
import java.util.List;

@Component
public class DetectionServiceClient {

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
        try {
            MultipartBodyBuilder bodyBuilder = new MultipartBodyBuilder();
            bodyBuilder.part("file", new ByteArrayResource(imageBytes) {
                @Override
                public String getFilename() {
                    return filename != null ? filename : "image.jpg";
                }
            }, MediaType.IMAGE_JPEG);

            return restClient.post()
                    .uri(detectionServiceUrl + "/predict?threshold=" + threshold)
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(bodyBuilder.build())
                    .retrieve()
                    .body(DetectionResponseDTO.class);
        } catch (Exception e) {
            throw new ServiceUnavailableException("RF-DETR Detection Service is currently unavailable: " + e.getMessage());
        }
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DetectionResponseDTO {
        @Builder.Default
        private List<DetectionItemDTO> detections = new ArrayList<>();
        private String damageType;
        private Double confidence;
        private List<Double> boundingBox;
        private int detectionCount;
        private int imageWidth;
        private int imageHeight;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DetectionItemDTO {
        private String damageType;
        private double confidence;
        private List<Double> boundingBox;
        private int classId;
    }
}
