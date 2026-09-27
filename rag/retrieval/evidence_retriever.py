import os
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
RAG_DEPLOYMENT_MODE = os.environ.get("RAG_DEPLOYMENT_MODE", "lightweight").lower()

# Check availability of heavy dependencies
HAS_CHROMADB = False
if RAG_DEPLOYMENT_MODE != "lightweight":
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer, util
        HAS_CHROMADB = True
    except ImportError:
        HAS_CHROMADB = False

_lightweight_retriever = None

if HAS_CHROMADB and RAG_DEPLOYMENT_MODE == "research":
    DB_PATH = os.path.join(BASE_DIR, "vectorstore", "chroma")
    MODEL_NAME = "all-MiniLM-L6-v2"
    MODEL = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        collection = client.get_collection("roadsense_knowledge")
    except Exception:
        collection = None
else:
    collection = None
    from retrieval.lightweight_retriever import LightweightRetriever
    _lightweight_retriever = LightweightRetriever()

def retrieve(
    query: str,
    k: int = 5,
    category_filter: Optional[str] = None,
    source_diversity: bool = True
) -> List[Dict[str, Any]]:
    """
    Retrieves top-k evidence chunks.
    Uses LightweightRetriever in deployment mode (< 5MB RAM, NO PyTorch/CUDA/ChromaDB),
    or ChromaDB in research evaluation mode.
    """
    if _lightweight_retriever is not None:
        return _lightweight_retriever.retrieve(
            query=query,
            k=k,
            category_filter=category_filter,
            source_diversity=source_diversity
        )

    if collection is None:
        return []

    where_clause = {}
    if category_filter:
        where_clause = {"category": category_filter}

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

    raw_evidence.sort(key=lambda x: x["score"], reverse=True)

    if not source_diversity:
        for idx, item in enumerate(raw_evidence[:k]):
            item["rank"] = idx + 1
        return raw_evidence[:k]

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

    if len(diversified) < k:
        for item in raw_evidence:
            if item not in diversified:
                diversified.append(item)
            if len(diversified) == k:
                break

    for idx, item in enumerate(diversified):
        item["rank"] = idx + 1

    return diversified