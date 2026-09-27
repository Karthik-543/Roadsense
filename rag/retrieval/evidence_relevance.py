import os
import re

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            _model = None
    return _model


def check_relevance(query, evidence, threshold=0.45):
    deployment_mode = os.environ.get("RAG_DEPLOYMENT_MODE", "lightweight").lower()
    model = get_model() if deployment_mode != "lightweight" else None

    if model is not None:
        from sentence_transformers import util
        query_embedding = model.encode(query, convert_to_tensor=True)
        validated = []
        for item in evidence:
            evidence_embedding = model.encode(
                item["text"],
                convert_to_tensor=True
            )
            relevance = float(
                util.cos_sim(query_embedding, evidence_embedding)[0][0]
            )
            item = item.copy()
            item["relevance_score"] = round(relevance, 4)
            item["relevant"] = relevance >= threshold
            validated.append(item)
        return validated

    validated = []
    stopwords = {"what", "is", "are", "the", "for", "a", "an", "in", "on", "to", "of", "and", "how", "does"}
    q_words = set(re.findall(r'\w+', query.lower())) - stopwords

    for item in evidence:
        item = item.copy()
        if "score" in item:
            relevance = float(item["score"])
        else:
            text_words = set(re.findall(r'\w+', item.get("text", "").lower())) - stopwords
            if q_words and text_words:
                relevance = len(q_words.intersection(text_words)) / max(len(q_words), 1)
            else:
                relevance = 0.0
        item["relevance_score"] = round(relevance, 4)
        item["relevant"] = relevance >= threshold
        validated.append(item)

    return validated