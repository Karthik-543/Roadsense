from typing import Dict, Any, List
from retrieval.evidence_retriever import retrieve
from retrieval.evidence_evaluator import evaluate_evidence
from retrieval.query_adapter import adapt_query

def adaptive_retrieve(
    query: str,
    k: int = 5,
    max_attempts: int = 2,
    min_score: float = 0.50
) -> Dict[str, Any]:
    """
    Multi-stage adaptive retrieval pipeline.
    Executes initial retrieval -> evaluates evidence -> reformulates query if insufficient
    -> executes secondary retrieval -> compares and merges evidence sets.
    """
    attempt_history = []

    # Attempt 1: Primary Query Retrieval
    evidence_1 = retrieve(query, k=k)
    eval_1 = evaluate_evidence(query, evidence_1, min_score=min_score)

    attempt_history.append({
        "attempt": 1,
        "query_used": query,
        "evidence_count": len(evidence_1),
        "top_score": eval_1["top_score"],
        "mean_score": eval_1["mean_score"],
        "sufficient": eval_1["sufficient"],
        "status": eval_1["status"],
        "reason": eval_1["reason"]
    })

    # If evidence is sufficient or query represents explicit image limitation, stop
    if eval_1["sufficient"] or eval_1["status"] == "INSUFFICIENT" and "cannot be determined" in eval_1["reason"]:
        return {
            "original_query": query,
            "final_query": query,
            "attempts": 1,
            "attempt_history": attempt_history,
            "evaluation": eval_1,
            "evidence": evidence_1,
            "evidence_status": eval_1["status"],
            "adaptation_occurred": False,
            "reason_for_adaptation": None
        }

    # Attempt 2: Adapted Query Retrieval
    adapted_query = adapt_query(query)
    evidence_2 = retrieve(adapted_query, k=k)
    eval_2 = evaluate_evidence(query, evidence_2, min_score=min_score)

    attempt_history.append({
        "attempt": 2,
        "query_used": adapted_query,
        "evidence_count": len(evidence_2),
        "top_score": eval_2["top_score"],
        "mean_score": eval_2["mean_score"],
        "sufficient": eval_2["sufficient"],
        "status": eval_2["status"],
        "reason": eval_2["reason"]
    })

    # Select best performing evidence set (or merge top chunks)
    if eval_2["top_score"] >= eval_1["top_score"]:
        selected_evidence = evidence_2
        selected_eval = eval_2
        final_query = adapted_query
    else:
        selected_evidence = evidence_1
        selected_eval = eval_1
        final_query = query

    return {
        "original_query": query,
        "final_query": final_query,
        "adapted_query": adapted_query,
        "attempts": 2,
        "attempt_history": attempt_history,
        "evaluation": selected_eval,
        "evidence": selected_evidence,
        "evidence_status": selected_eval["status"],
        "adaptation_occurred": True,
        "reason_for_adaptation": f"Attempt 1 evidence status was {eval_1['status']} (top score {eval_1['top_score']} < threshold {min_score}). Query expanded."
    }

if __name__ == "__main__":
    q = "What is the recommended treatment for potholes?"
    res = adaptive_retrieve(q)
    print("Adaptive Retrieve Result:")
    print(f"Attempts: {res['attempts']}")
    print(f"Status: {res['evidence_status']}")
    print(f"Final Query: {res['final_query']}")
    print(f"Top Score: {res['evaluation']['top_score']}")