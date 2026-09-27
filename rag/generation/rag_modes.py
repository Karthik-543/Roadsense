import time
from typing import Dict, Any, Optional
from retrieval.case_context import CaseContextBuilder
from retrieval.evidence_retriever import retrieve
from retrieval.evidence_evaluator import evaluate_evidence
from retrieval.adaptive_retriever import adaptive_retrieve
from retrieval.claim_verifier import ClaimVerifier
from generation.llm_interface import LLMInterface

class RAGPipeline:
    """
    Executes RoadSense AI assessments across the four experimental modes:
    - MODE A: NO_RAG
    - MODE B: STANDARD_RAG
    - MODE C: EVIDENCE_AWARE_RAG
    - MODE D: EVIDENCE_AWARE_ADAPTIVE_RAG
    """

    def __init__(self, llm_provider: str = "auto"):
        self.context_builder = CaseContextBuilder()
        self.claim_verifier = ClaimVerifier()
        self.llm = LLMInterface(provider=llm_provider)

    def run_assessment(
        self,
        query: str,
        detector_results: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, Any]] = None,
        weather: Optional[Dict[str, Any]] = None,
        traffic: Optional[Dict[str, Any]] = None,
        mode: str = "evidence_aware_adaptive",
        k: int = 5
    ) -> Dict[str, Any]:
        
        start_time = time.time()
        mode_upper = mode.upper()

        # Build standardized case context payload
        case_context = self.context_builder.build_context(
            detector_results=detector_results,
            location=location,
            weather=weather,
            traffic=traffic
        )

        evidence_chunks = []
        evidence_eval = {}
        retrieval_attempts = 1
        adaptation_occurred = False
        adapted_query = None

        if mode_upper == "NO_RAG":
            evidence_chunks = []
            evidence_eval = {
                "top_score": 0.0,
                "mean_score": 0.0,
                "strong_hits": 0,
                "sufficient": False,
                "status": "NO_RAG"
            }
        elif mode_upper == "STANDARD_RAG":
            evidence_chunks = retrieve(query, k=k, source_diversity=False)
            evidence_eval = evaluate_evidence(query, evidence_chunks)
        elif mode_upper == "EVIDENCE_AWARE_RAG":
            evidence_chunks = retrieve(query, k=k, source_diversity=True)
            evidence_eval = evaluate_evidence(query, evidence_chunks)
        elif mode_upper == "EVIDENCE_AWARE_ADAPTIVE_RAG" or mode_upper == "EVIDENCE_AWARE_ADAPTIVE":
            adapt_res = adaptive_retrieve(query, k=k)
            evidence_chunks = adapt_res["evidence"]
            evidence_eval = adapt_res["evaluation"]
            retrieval_attempts = adapt_res["attempts"]
            adaptation_occurred = adapt_res["adaptation_occurred"]
            adapted_query = adapt_res.get("adapted_query")
        else:
            raise ValueError(f"Unknown RAG mode: {mode}")

        # LLM Report Generation
        raw_report = self.llm.generate_report(case_context, evidence_chunks, rag_mode=mode_upper)

        # Claim Verification & Citation Provenance
        if mode_upper in ["EVIDENCE_AWARE_RAG", "EVIDENCE_AWARE_ADAPTIVE_RAG", "EVIDENCE_AWARE_ADAPTIVE"]:
            verification_result = self.claim_verifier.verify_and_inject_citations(raw_report, evidence_chunks)
        else:
            # Baseline modes skip structured claim verification
            claims = self.claim_verifier.extract_claims(raw_report)
            verification_result = {
                "total_claims": len(claims),
                "supported_claims": len(claims) if mode_upper != "NO_RAG" else 0,
                "unsupported_claims": 0 if mode_upper != "NO_RAG" else len(claims),
                "unsupported_claim_rate": 0.0 if mode_upper != "NO_RAG" else 1.0,
                "claims": []
            }

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query,
            "rag_mode": mode_upper,
            "latency_ms": latency_ms,
            "retrieval_attempts": retrieval_attempts,
            "adaptation_occurred": adaptation_occurred,
            "adapted_query": adapted_query,
            "case_context": case_context,
            "evidence": evidence_chunks,
            "evidence_evaluation": evidence_eval,
            "verification": verification_result,
            "report": raw_report,
            "sources": [
                {
                    "source_id": e.get("source_id"),
                    "title": e.get("source_title"),
                    "page": e.get("page"),
                    "chunk_id": e.get("chunk_id")
                }
                for e in evidence_chunks
            ]
        }

if __name__ == "__main__":
    pipeline = RAGPipeline()
    res = pipeline.run_assessment(
        query="What maintenance treatment is recommended for potholes?",
        detector_results={"damage_class": "pothole", "confidence": 0.95},
        location={"latitude": 13.08, "longitude": 80.27},
        weather={"rainfall_mm": 20.0},
        traffic={"route": "NH-48", "volume_level": "High"},
        mode="EVIDENCE_AWARE_ADAPTIVE_RAG"
    )
    print("Execution Mode:", res["rag_mode"])
    print("Latency:", res["latency_ms"], "ms")
    print("Retrieved Chunks:", len(res["evidence"]))
    print("Supported Claims:", res["verification"]["supported_claims"], "/", res["verification"]["total_claims"])
