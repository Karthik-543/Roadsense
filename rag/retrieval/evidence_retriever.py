import os
from pathlib import Path
import chromadb
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, util

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "vectorstore", "chroma")

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(path=DB_PATH)

try:
    collection = client.get_collection("roadsense_knowledge")
except Exception:
    collection = None

def retrieve(
    query: str,
    k: int = 5,
    category_filter: Optional[str] = None,
    source_diversity: bool = True
) -> List[Dict[str, Any]]:
    """
    Retrieves top-k evidence chunks from ChromaDB.
    Supports similarity scoring, metadata filtering, and source diversity.
    """
    if collection is None:
        return []

    # Prepare metadata query filter if category provided
    where_clause = {}
    if category_filter:
        where_clause = {"category": category_filter}

    # Fetch initial pool (oversample if diversity requested)
    fetch_n = k * 2 if source_diversity else k

    try:
        query_vec = MODEL.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_vec],
            n_results=min(fetch_n, max(collection.count(), 1)),
            where=where_clause if where_clause else None
        )
    except Exception as e:
        print(f"Retrieval query error: {e}")
        return []

    if not results or not results["documents"] or not results["documents"][0]:
        return []

    documents = results["documents"][0]
    metadata = results["metadatas"][0]
    ids = results["ids"][0]

    query_embedding = MODEL.encode(query, convert_to_tensor=True)
    doc_embeddings = MODEL.encode(documents, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, doc_embeddings)[0]

    raw_evidence = []
    for i, (text, meta, score, c_id) in enumerate(zip(documents, metadata, scores, ids)):
        raw_evidence.append({
            "score": round(float(score), 4),
            "chunk_id": c_id,
            "source_id": meta.get("source_id", meta.get("document")),
            "source_title": meta.get("source_title", meta.get("document")),
            "organization": meta.get("organization", "Unknown"),
            "year": meta.get("year", "Unknown"),
            "document": meta.get("document"),
            "page": meta.get("page", 1),
            "section": meta.get("section", "General"),
            "category": meta.get("category", "general"),
            "official_url": meta.get("official_url", ""),
            "provenance": meta.get("provenance", f"{meta.get('document')}, p. {meta.get('page')}"),
            "text": text
        })

    # Sort descending by cosine similarity score
    raw_evidence.sort(key=lambda x: x["score"], reverse=True)

    if not source_diversity:
        for idx, item in enumerate(raw_evidence[:k]):
            item["rank"] = idx + 1
        return raw_evidence[:k]

    # Source-aware diversity filtering: limit max chunks per single source to 2 unless total sources < k
    diversified = []
    source_counts = {}

    for item in raw_evidence:
        src = item["source_id"]
        count = source_counts.get(src, 0)
        if count < 2 or len(source_counts) < 2:
            diversified.append(item)
            source_counts[src] = count + 1
        if len(diversified) == k:
            break

    # If diversification resulted in fewer than k items, fill remaining from raw_evidence
    if len(diversified) < k:
        for item in raw_evidence:
            if item not in diversified:
                diversified.append(item)
            if len(diversified) == k:
                break

    for idx, item in enumerate(diversified):
        item["rank"] = idx + 1

    return diversified

if __name__ == "__main__":
    query = "What maintenance treatment is recommended for potholes?"
    res = retrieve(query, k=5, source_diversity=True)
    print(f"Retrieved {len(res)} chunks for: '{query}'")
    for r in res:
        print(f"Rank {r['rank']} | Score: {r['score']} | Source: {r['source_title']} (p. {r['page']})")