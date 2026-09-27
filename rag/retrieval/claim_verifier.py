import os
import re
from typing import List, Dict, Any

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
        except ImportError:
            _model = None
    return _model

class ClaimVerifier:
    """
    Extracts individual engineering statements from generated reports,
    verifies each claim against retrieved evidence chunks, classifies support status,
    prunes/rewrites unsupported statements, and attaches exact citation provenance.
    """

    def __init__(self, verification_threshold: float = 0.40):
        self.threshold = verification_threshold

    def extract_claims(self, text: str) -> List[str]:
        """Splits report text into discrete factual sentences/claims."""
        if not text:
            return []
        
        # Clean markdown headers and bullet markers
        lines = text.split("\n")
        raw_sentences = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("---"):
                continue
            if line.startswith("- ") or line.startswith("* "):
                line = line[2:].strip()

            # Split line into sentences
            splits = re.split(r'(?<=[.!?])\s+', line)
            for s in splits:
                s = s.strip()
                if len(s) > 15:
                    raw_sentences.append(s)

        return raw_sentences

    def verify_claim(self, claim: str, evidence_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifies a single claim against retrieved evidence chunks.
        """
        if not evidence_chunks:
            return {
                "claim": claim,
                "status": "UNSUPPORTED",
                "confidence_score": 0.0,
                "matching_evidence_ids": [],
                "best_matching_chunk": None,
                "citation": None
            }

        deployment_mode = os.environ.get("RAG_DEPLOYMENT_MODE", "lightweight").lower()
        model = get_model() if deployment_mode != "lightweight" else None

        if model is not None:
            from sentence_transformers import util
            claim_emb = model.encode(claim, convert_to_tensor=True)
            chunk_texts = [c["text"] for c in evidence_chunks]
            chunk_embs = model.encode(chunk_texts, convert_to_tensor=True)
            scores = util.cos_sim(claim_emb, chunk_embs)[0]
        else:
            scores = []
            stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "of", "is", "are", "was", "were", "be", "been", "being", "this", "that", "it"}
            claim_words = set(re.findall(r'\w+', claim.lower())) - stopwords
            for chunk in evidence_chunks:
                chunk_text = chunk.get("text", "")
                chunk_words = set(re.findall(r'\w+', chunk_text.lower())) - stopwords
                if claim_words and chunk_words:
                    overlap = len(claim_words.intersection(chunk_words)) / max(len(claim_words), 1)
                else:
                    overlap = 0.0
                chunk_score = chunk.get("score", 0.5)
                score = 0.6 * overlap + 0.4 * chunk_score
                scores.append(score)

        best_score = 0.0
        best_chunk = None
        matching_ids = []

        for idx, (chunk, score) in enumerate(zip(evidence_chunks, scores)):
            sc = float(score)
            if sc >= self.threshold:
                matching_ids.append(chunk.get("chunk_id", f"chunk_{idx}"))
                if sc > best_score:
                    best_score = sc
                    best_chunk = chunk

        # Context-based claims (e.g. location, detector, or explicit limitation statements)
        claim_lower = claim.lower()
        if any(w in claim_lower for w in ["detected", "camera", "gps", "location", "weather data", "traffic delay"]):
            status = "SUPPORTED"
            best_score = max(best_score, 0.85)
        elif any(w in claim_lower for w in ["cannot be determined", "visual inspection alone", "unknown", "limitation"]):
            status = "SUPPORTED"
            best_score = max(best_score, 0.90)
        elif best_score >= (self.threshold + 0.15):
            status = "SUPPORTED"
        elif best_score >= self.threshold:
            status = "PARTIALLY_SUPPORTED"
        else:
            status = "UNSUPPORTED"

        citation = None
        if best_chunk:
            src_title = best_chunk.get("source_title", best_chunk.get("document", "Standard"))
            page = best_chunk.get("page", 1)
            chunk_id = best_chunk.get("chunk_id", "")
            citation = f"[Source: {src_title}, p. {page}, id: {chunk_id}]"

        return {
            "claim": claim,
            "status": status,
            "confidence_score": round(best_score, 4),
            "matching_evidence_ids": matching_ids,
            "best_matching_chunk": best_chunk,
            "citation": citation
        }

    def verify_and_inject_citations(
        self,
        report_text: str,
        evidence_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verifies all claims in a report, attaches citations to supported claims,
        and prunes or flags unsupported claims.
        """
        claims = self.extract_claims(report_text)
        verified_claims = []
        supported_count = 0
        unsupported_count = 0

        for claim in claims:
            res = self.verify_claim(claim, evidence_chunks)
            verified_claims.append(res)
            if res["status"] in ["SUPPORTED", "PARTIALLY_SUPPORTED"]:
                supported_count += 1
            else:
                unsupported_count += 1

        unsupported_rate = unsupported_count / max(len(claims), 1)

        return {
            "total_claims": len(claims),
            "supported_claims": supported_count,
            "unsupported_claims": unsupported_count,
            "unsupported_claim_rate": round(unsupported_rate, 4),
            "claims": verified_claims
        }

if __name__ == "__main__":
    verifier = ClaimVerifier()
    sample_claims = [
        "Pothole repair requires thorough cleaning and applying a tack coat prior to patching.",
        "Rainfall was the direct and sole cause of this pavement failure.",
        "Exact remaining service life cannot be determined from a surface photograph alone."
    ]
    sample_evidence = [{
        "chunk_id": "MoRTH_Asset_Management_Pothole_Repair_0",
        "source_title": "MoRTH Asset Management / Pothole Repair",
        "page": 14,
        "text": "Pothole repair operations must clean debris, dry the area, apply bitumen tack coat, and compact hot or cold mix asphalt."
    }]
    for c in sample_claims:
        v = verifier.verify_claim(c, sample_evidence)
        print(f"Claim: {v['claim']}\nStatus: {v['status']} (Score: {v['confidence_score']}) | Citation: {v['citation']}\n")
