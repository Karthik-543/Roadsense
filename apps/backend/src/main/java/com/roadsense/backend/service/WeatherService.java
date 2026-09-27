package com.roadsense.backend.service;

import com.roadsense.backend.model.Assessment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.time.LocalDate;

import java.util.*;

@Service
public class WeatherService {

    private static final Logger logger = LoggerFactory.getLogger(WeatherService.class);

    private final RestClient restClient;
    private final String openMeteoUrl;

    public WeatherService(
            RestClient restClient,
            @Value("${services.open-meteo.url}") String openMeteoUrl
    ) {
        this.restClient = restClient;
        this.openMeteoUrl = openMeteoUrl;
    }

    public Assessment.WeatherContext getWeatherContext(Double lat, Double lon) {
        if (lat == null || lon == null) {
            return Assessment.WeatherContext.builder()
                    .available(false)
                    .retrievedAt(Instant.now())
                    .environmentalNote("Weather context unavailable due to missing GPS location coordinates.")
                    .build();
        }

        LocalDate today = LocalDate.now();
        List<Assessment.WeatherDay> historical = new ArrayList<>();
        List<Assessment.WeatherDay> forecast = new ArrayList<>();

        try {
            String uri = String.format(
                    "%s?latitude=%.4f&longitude=%.4f&past_days=7&forecast_days=7&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=auto",
                    openMeteoUrl, lat, lon
            );

            Map<String, Object> response = restClient.get()
                    .uri(uri)
                    .retrieve()
                    .body(Map.class);

            if (response != null && response.containsKey("daily")) {
                Map<String, Object> daily = (Map<String, Object>) response.get("daily");
                List<String> dates = (List<String>) daily.get("time");
                List<Number> precips = (List<Number>) daily.get("precipitation_sum");
                List<Number> maxTemps = (List<Number>) daily.get("temperature_2m_max");
                List<Number> minTemps = (List<Number>) daily.get("temperature_2m_min");

                if (dates != null) {
                    for (int i = 0; i < dates.size(); i++) {
                        String dateStr = dates.get(i);
                        LocalDate d = LocalDate.parse(dateStr);
                        double pr = precips != null && i < precips.size() && precips.get(i) != null ? precips.get(i).doubleValue() : 0.0;
                        double tMax = maxTemps != null && i < maxTemps.size() && maxTemps.get(i) != null ? maxTemps.get(i).doubleValue() : 28.0;
                        double tMin = minTemps != null && i < minTemps.size() && minTemps.get(i) != null ? minTemps.get(i).doubleValue() : 20.0;

                        boolean isFcst = d.isAfter(today.minusDays(1));

                        Assessment.WeatherDay day = Assessment.WeatherDay.builder()
                                .date(dateStr)
                                .precipitationMm(pr)
                                .tempMaxC(tMax)
                                .tempMinC(tMin)
                                .condition(pr > 10.0 ? "Heavy Rain" : (pr > 2.0 ? "Moderate Rain" : "Clear / Dry"))
                                .isForecast(isFcst)
                                .build();

                        if (isFcst) {
                            forecast.add(day);
                        } else {
                            historical.add(day);
                        }
                    }
                }
            }
        } catch (Exception e) {
            logger.warn("Open-Meteo weather API call failed: {}", e.getMessage());
        }

        double totalHistPrecip = historical.stream()
                .mapToDouble(d -> d.getPrecipitationMm() != null ? d.getPrecipitationMm() : 0.0)
                .sum();

        String note = String.format(
                "Recent 7-day cumulative precipitation: %.1f mm. " +
                "Environmental moisture conditions are evaluated as a contributing factor associated with pavement deterioration. " +
                "Available context does NOT establish rainfall as the sole or definitive cause of damage.",
                totalHistPrecip
        );

        return Assessment.WeatherContext.builder()
                .available(!historical.isEmpty() || !forecast.isEmpty())
                .historical7Days(historical)
                .forecast7Days(forecast)
                .retrievedAt(Instant.now())
                .environmentalNote(note)
                .build();
    }
}
