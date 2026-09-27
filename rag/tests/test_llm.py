import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from generation.llm_interface import LLMInterface
from generation.rag_modes import RAGPipeline
from api.app import app, get_config
from fastapi.testclient import TestClient

class TestRoadSenseLLMIntegration(unittest.TestCase):

    def setUp(self):
        # Ensure clean env state for predictable tests
        self.original_api_key = os.environ.get("OPENAI_API_KEY")
        self.original_model = os.environ.get("OPENAI_MODEL")

    def tearDown(self):
        if self.original_api_key is not None:
            os.environ["OPENAI_API_KEY"] = self.original_api_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        if self.original_model is not None:
            os.environ["OPENAI_MODEL"] = self.original_model
        elif "OPENAI_MODEL" in os.environ:
            del os.environ["OPENAI_MODEL"]

        from api.app import pipeline
        pipeline.llm = LLMInterface()

    def test_llm_config_loading(self):
        os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        llm = LLMInterface()
        self.assertEqual(llm.model_name, "gpt-4o-mini")
        self.assertEqual(llm.active_provider, "deterministic_engineering_engine")

    def test_missing_api_key_triggers_fallback(self):
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        llm = LLMInterface(provider="auto")
        sample_context = {
            "query": "Pothole assessment",
            "observations": [{"damage_class": "pothole", "confidence": 0.92}],
            "location_context": {"available": True, "mapped_road": "NH-44"},
            "weather_context": {"available": True, "rainfall_mm": 15.0},
            "traffic_context": {"available": True, "traffic_volume_level": "High"}
        }
        report = llm.generate_report(sample_context, [], rag_mode="EVIDENCE_AWARE_ADAPTIVE_RAG")

        self.assertIn("## OBSERVED DAMAGE", report)
        self.assertIn("## LOCATION CONTEXT", report)
        self.assertIn("## WEATHER CONTEXT", report)
        self.assertIn("## ASSESSMENT", report)
        self.assertEqual(llm.active_provider, "deterministic_engineering_engine")

    @patch("openai.OpenAI")
    def test_mock_openai_llm_generation_integrated(self, mock_openai_cls):
        os.environ["OPENAI_API_KEY"] = "sk-test-mock-key"
        os.environ["OPENAI_MODEL"] = "gpt-4o-mini"

        # Setup mock completion response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="## OBSERVED DAMAGE\n- Pothole observed\n\n## ASSESSMENT\n- Repair indicated per MoRTH standards."))
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_cls.return_value = mock_client

        pipeline = RAGPipeline(llm_provider="auto")
        res = pipeline.run_assessment(
            query="What repair method applies to potholes?",
            detector_results={"damage_class": "pothole", "confidence": 0.95},
            mode="EVIDENCE_AWARE_ADAPTIVE_RAG",
            k=3
        )

        self.assertIn("Pothole observed", res["report"])
        self.assertIn("MoRTH standards", res["report"])
        self.assertIn("sources", res)
        self.assertIn("verification", res)

    @patch("openai.OpenAI")
    def test_openai_api_error_triggers_fallback(self, mock_openai_cls):
        os.environ["OPENAI_API_KEY"] = "sk-test-invalid-key"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Authentication failed or quota exceeded")
        mock_openai_cls.return_value = mock_client

        llm = LLMInterface(provider="openai")
        sample_context = {
            "query": "Transverse crack analysis",
            "observations": [{"damage_class": "transverse_crack", "confidence": 0.88}],
            "location_context": {"available": False},
            "weather_context": {"available": False},
            "traffic_context": {"available": False}
        }

        # Should NOT raise an exception, but fall back gracefully
        report = llm.generate_report(sample_context, [], rag_mode="STANDARD_RAG")
        self.assertIn("## OBSERVED DAMAGE", report)
        self.assertIn("Transverse_crack", report)

    def test_api_response_does_not_contain_api_key(self):
        secret_key = "TEST_API_KEY_PLACEHOLDER"
        os.environ["OPENAI_API_KEY"] = secret_key

        from api.app import pipeline
        pipeline.llm = LLMInterface()

        client = TestClient(app)

        # Config endpoint check
        cfg_resp = client.get("/api/v1/config")
        self.assertEqual(cfg_resp.status_code, 200)
        cfg_data = cfg_resp.json()

        self.assertNotIn(secret_key, str(cfg_data))
        self.assertNotIn("OPENAI_API_KEY", cfg_data)
        self.assertTrue(cfg_data["llm_enabled"])

        # Health endpoint check
        health_resp = client.get("/api/v1/health")
        self.assertNotIn(secret_key, str(health_resp.json()))

    def test_existing_provenance_and_citations_intact(self):
        pipeline = RAGPipeline()
        res = pipeline.run_assessment(
            query="What standard repair procedures apply to severe alligator cracking?",
            mode="EVIDENCE_AWARE_ADAPTIVE_RAG",
            k=3
        )
        self.assertGreater(len(res["sources"]), 0)
        first_source = res["sources"][0]
        self.assertIn("source_id", first_source)
        self.assertIn("title", first_source)
        self.assertIn("page", first_source)

if __name__ == "__main__":
    unittest.main()
