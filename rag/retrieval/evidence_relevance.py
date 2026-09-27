from sentence_transformers import SentenceTransformer, util

MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def check_relevance(query, evidence, threshold=0.45):
    query_embedding = MODEL.encode(query, convert_to_tensor=True)

    validated = []

    for item in evidence:
        evidence_embedding = MODEL.encode(
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