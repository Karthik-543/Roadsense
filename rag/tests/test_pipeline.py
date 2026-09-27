import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from retrieval.case_context import CaseContextBuilder
from retrieval.evidence_retriever import retrieve
from retrieval.evidence_evaluator import evaluate_evidence
from retrieval.query_adapter import adapt_query
from retrieval.adaptive_retriever import adaptive_retrieve
from retrieval.claim_verifier import ClaimVerifier
from generation.llm_interface import LLMInterface
from generation.rag_modes import RAGPipeline

class TestRoadSenseRAGPipeline(unittest.TestCase):

    def setUp(self):
        self.context_builder = CaseContextBuilder()
        self.verifier = ClaimVerifier()
        self.pipeline = RAGPipeline()

    def test_case_context_missing_weather_and_traffic(self):
        ctx = self.context_builder.build_context(
            detector_results={"damage_class": "pothole", "confidence": 0.95},
            location={"latitude": 12.97, "longitude": 77.59, "mapped_road": "NH-44"}
        )
        self.assertTrue(ctx["location_context"]["available"])
        self.assertFalse(ctx["weather_context"]["available"])
        self.assertFalse(ctx["traffic_context"]["available"])
        self.assertIn("unavailable", ctx["weather_context"]["note"])

    def test_case_context_non_causal_weather_and_traffic_notes(self):
        ctx = self.context_builder.build_context(
            weather={"rainfall_mm": 50.0},
            traffic={"volume_level": "High", "route": "NH-44 Corridor"}
        )
        self.assertIn("may be an environmental factor", ctx["weather_context"]["engineering_note"])
        self.assertNotIn("rainfall caused", ctx["weather_context"]["engineering_note"].lower())
        self.assertIn("does NOT establish direct physical causation", ctx["traffic_context"]["operational_note"])

    def test_query_adapter_deterministic_expansion(self):
        orig = "What is the repair method for potholes?"
        adapted = adapt_query(orig)
        self.assertIn("patch repair", adapted)
        self.assertIn("MoRTH guidelines", adapted)

    def test_evidence_evaluator_limitation_query(self):
        query = "What exact remaining service life can be determined from a single pothole image?"
        evidence = retrieve(query, k=5)
        eval_res = evaluate_evidence(query, evidence)
        self.assertFalse(eval_res["sufficient"])
        self.assertEqual(eval_res["status"], "INSUFFICIENT")
        self.assertIn("cannot be determined", eval_res["reason"])

    def test_adaptive_retrieval(self):
        query = "What maintenance treatment is recommended for potholes?"
        res = adaptive_retrieve(query, k=5)
        self.assertIn(res["evidence_status"], ["SUPPORTED", "PARTIALLY_SUPPORTED"])
        self.assertGreater(len(res["evidence"]), 0)

    def test_claim_verifier_and_citation_injection(self):
        sample_report = "Pothole repair requires thorough cleaning and applying a tack coat prior to asphalt compaction."
        sample_evidence = [{
            "chunk_id": "MoRTH_Asset_Management_Pothole_Repair_0",
            "source_title": "MoRTH Asset Management / Pothole Repair",
            "organization": "MoRTH",
            "year": "2021",
            "page": 14,
            "text": "Pothole repair operations must clean debris, dry the area, apply bitumen tack coat, and compact hot or cold mix asphalt."
        }]
        res = self.verifier.verify_and_inject_citations(sample_report, sample_evidence)
        self.assertGreater(res["supported_claims"], 0)
        self.assertEqual(res["unsupported_claim_rate"], 0.0)

    def test_rag_modes_execution(self):
        for mode in ["NO_RAG", "STANDARD_RAG", "EVIDENCE_AWARE_RAG", "EVIDENCE_AWARE_ADAPTIVE_RAG"]:
            res = self.pipeline.run_assessment(
                query="What maintenance treatment is recommended for potholes?",
                mode=mode,
                k=5
            )
            self.assertEqual(res["rag_mode"], mode)
            self.assertIn("report", res)
            self.assertIn("latency_ms", res)

if __name__ == "__main__":
    unittest.main()
