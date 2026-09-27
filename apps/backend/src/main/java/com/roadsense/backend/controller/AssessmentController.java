package com.roadsense.backend.controller;

import com.roadsense.backend.model.Assessment;
import com.roadsense.backend.service.AssessmentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/assessments")
public class AssessmentController {

    private final AssessmentService assessmentService;

    public AssessmentController(AssessmentService assessmentService) {
        this.assessmentService = assessmentService;
    }

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Assessment> createAssessment(
            Authentication authentication,
            @RequestPart("file") MultipartFile file,
            @RequestParam(value = "latitude", required = false) Double latitude,
            @RequestParam(value = "longitude", required = false) Double longitude,
            @RequestParam(value = "threshold", required = false, defaultValue = "0.3") Double threshold
    ) {
        String userId = (String) authentication.getPrincipal();
        Assessment assessment = assessmentService.createAssessment(userId, file, latitude, longitude, threshold);
        return new ResponseEntity<>(assessment, HttpStatus.CREATED);
    }

    @PostMapping(value = "/{assessmentId}/images", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Assessment> addAdditionalImage(
            Authentication authentication,
            @PathVariable("assessmentId") String assessmentId,
            @RequestPart("file") MultipartFile file,
            @RequestParam(value = "threshold", required = false, defaultValue = "0.3") Double threshold
    ) {
        String userId = (String) authentication.getPrincipal();
        Assessment updated = assessmentService.addAdditionalImage(assessmentId, userId, file, threshold);
        return ResponseEntity.ok(updated);
    }

    @GetMapping
    public ResponseEntity<List<Assessment>> getUserAssessments(Authentication authentication) {
        String userId = (String) authentication.getPrincipal();
        List<Assessment> list = assessmentService.getUserAssessments(userId);
        return ResponseEntity.ok(list);
    }

    @GetMapping("/{assessmentId}")
    public ResponseEntity<Assessment> getAssessmentDetails(
            Authentication authentication,
            @PathVariable("assessmentId") String assessmentId
    ) {
        String userId = (String) authentication.getPrincipal();
        Assessment assessment = assessmentService.getAssessment(assessmentId, userId);
        return ResponseEntity.ok(assessment);
    }
}
