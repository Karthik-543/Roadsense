from typing import List, Dict, Any

# Standard negative evidence triggers for image limitation queries
IMAGE_LIMITATION_PATTERNS = [
    "exact remaining service life",
    "exact repair cost",
    "structural load carrying capacity",
    "exact cost of repairing",
    "sub-surface structural load",
    "exact pavement layer failure depth"
]

def evaluate_evidence(
    query: str,
    evidence: List[Dict[str, Any]],
    min_score: float = 0.50,
    min_hits: int = 2
) -> Dict[str, Any]:
    """
    Evaluates retrieved evidence to determine evidence sufficiency and support status.
    Considers relevance scores, hit count, source diversity, and query claim constraints.
    """
    if not evidence:
        return {
            "top_score": 0.0,
            "mean_score": 0.0,
            "strong_hits": 0,
            "source_diversity_count": 0,
            "sufficient": False,
            "status": "INSUFFICIENT",
            "reason": "No evidence retrieved."
        }

    scores = [x["score"] for x in evidence]
    top_score = round(max(scores), 4)
    mean_score = round(sum(scores) / len(scores), 4)

    strong_hits = [x for x in evidence if x["score"] >= min_score]
    sources = set(x["source_id"] for x in evidence if x["score"] >= min_score)
    source_diversity_count = len(sources)

    # Check for explicit image limitation questions
    query_l = query.lower()
    is_limitation_query = any(pattern in query_l for pattern in IMAGE_LIMITATION_PATTERNS)

    if is_limitation_query:
        return {
            "top_score": top_score,
            "mean_score": mean_score,
            "strong_hits": len(strong_hits),
            "source_diversity_count": source_diversity_count,
            "sufficient": False,
            "status": "INSUFFICIENT",
            "reason": (
                "Query requests quantitative/structural parameters (e.g. exact cost, "
                "remaining service life, structural load capacity) that cannot be determined "
                "from image-based visual assessment alone."
            )
        }

    # Evaluate sufficiency based on top_score and strong hit count
    if len(strong_hits) >= min_hits and top_score >= (min_score + 0.05):
        status = "SUPPORTED"
        sufficient = True
        reason = f"Strong evidence support ({len(strong_hits)} hits >= threshold {min_score}, top score {top_score})."
    elif len(strong_hits) >= 1 or top_score >= min_score:
        status = "PARTIALLY_SUPPORTED"
        sufficient = False # Triggers adaptive retrieval for secondary search refinement
        reason = f"Partial evidence found (top score {top_score}, strong hits {len(strong_hits)})."
    else:
        status = "INSUFFICIENT"
        sufficient = False
        reason = f"Insufficient evidence support (top score {top_score} < threshold {min_score})."

    return {
        "top_score": top_score,
        "mean_score": mean_score,
        "strong_hits": len(strong_hits),
        "source_diversity_count": source_diversity_count,
        "sufficient": sufficient,
        "status": status,
        "reason": reason
    }

if __name__ == "__main__":
    from retrieval.evidence_retriever import retrieve
    q1 = "What maintenance treatment is recommended for potholes?"
    ev1 = retrieve(q1, k=5)
    eval1 = evaluate_evidence(q1, ev1)
    print("Q1 Eval:", eval1)

    q2 = "What exact remaining service life can be determined from a single pothole image?"
    ev2 = retrieve(q2, k=5)
    eval2 = evaluate_evidence(q2, ev2)
    print("Q2 Eval (Limitation Case):", eval2)