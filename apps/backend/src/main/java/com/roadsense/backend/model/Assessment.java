package com.roadsense.backend.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "assessments")
public class Assessment {

    @Id
    private String id;

    @Indexed(unique = true)
    private String assessmentId;

    @Indexed
    private String userId;

    @Builder.Default
    private List<AssessmentImage> images = new ArrayList<>();

    private LocationContext location;

    private WeatherContext weather;

    private TrafficContext traffic;

    private RagAssessmentReport rag;

    @CreatedDate
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;

    // Embedded Value Objects

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AssessmentImage {
        private String imageId;
        private String filename;
        private String storagePath;
        private int width;
        private int height;
        @Builder.Default
        private List<DetectionResult> detections = new ArrayList<>();
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DetectionResult {
        private String damageType;
        private double confidence;
        private List<Double> boundingBox;
        private int classId;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LocationContext {
        private Double latitude;
        private Double longitude;
        private String address;
        private String road;
        private String roadType;
        private Map<String, Object> osmMetadata;
        @Builder.Default
        private List<NearbyFacility> nearbyInfrastructure = new ArrayList<>();
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class NearbyFacility {
        private String type; // school, hospital, bus_stop, junction
        private String name;
        private Double distanceMeters;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class WeatherContext {
        private boolean available;
        @Builder.Default
        private List<WeatherDay> historical7Days = new ArrayList<>();
        @Builder.Default
        private List<WeatherDay> forecast7Days = new ArrayList<>();
        private Instant retrievedAt;
        private String environmentalNote;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class WeatherDay {
        private String date;
        private Double precipitationMm;
        private Double tempMaxC;
        private Double tempMinC;
        private String condition;
        private boolean isForecast;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrafficContext {
        private boolean available;
        private Instant timestamp;
        private Integer durationSeconds;
        private Integer staticDurationSeconds;
        private Integer trafficDelaySeconds;
        private String trafficVolumeLevel;
        private String routeSummary;
        private String operationalNote;
        private Map<String, Object> rawApiData;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RagAssessmentReport {
        private String query;
        private String ragMode;
        private String report;
        private String executiveSummary;
        private String engineeringAssessment;
        @Builder.Default
        private List<String> recommendations = new ArrayList<>();
        @Builder.Default
        private List<String> uncertainties = new ArrayList<>();
        @Builder.Default
        private List<CitationItem> citations = new ArrayList<>();
        private Map<String, Object> claimVerification;
        private Double latencyMs;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CitationItem {
        private String sourceId;
        private String title;
        private int page;
        private String chunkId;
    }
}
