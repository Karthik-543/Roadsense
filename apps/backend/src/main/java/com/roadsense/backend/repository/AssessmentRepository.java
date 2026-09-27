package com.roadsense.backend.repository;

import com.roadsense.backend.model.Assessment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AssessmentRepository extends MongoRepository<Assessment, String> {
    Optional<Assessment> findByAssessmentId(String assessmentId);
    Optional<Assessment> findByAssessmentIdAndUserId(String assessmentId, String userId);
    List<Assessment> findByUserIdOrderByCreatedAtDesc(String userId);
    Page<Assessment> findByUserId(String userId, Pageable pageable);
}
