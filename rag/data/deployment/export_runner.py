import json
from pathlib import Path
import numpy as np

# Resolve BASE_DIR to the root rag folder (D:\projects\Roadsense\rag)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_EMBEDDINGS = BASE_DIR / "data" / "processed" / "embeddings.json"
DEPLOYMENT_DIR = BASE_DIR / "data" / "deployment"
DEPLOYMENT_DIR.mkdir(parents=True, exist_ok=True)

NPY_OUT = DEPLOYMENT_DIR / "embeddings.npy"
META_OUT = DEPLOYMENT_DIR / "chunks_metadata.json"

def run_export():
    print(f"Target input embeddings path: {INPUT_EMBEDDINGS}")
    if not INPUT_EMBEDDINGS.exists():
        print(f"File {INPUT_EMBEDDINGS} not found.")
        return

    with open(INPUT_EMBEDDINGS, "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings_list = []
    metadata_list = []

    for idx, item in enumerate(data):
        emb = item.get("embedding")
        embeddings_list.append(emb)

        doc_name = item.get("document", "unknown.txt")
        chunk_id = str(item.get("chunk_id", f"{doc_name}_{idx}"))
        meta = {
            "chunk_id": chunk_id,
            "document": doc_name,
            "source_id": str(item.get("source_id", doc_name)),
            "source_title": str(item.get("source_title", doc_name)),
            "organization": str(item.get("organization", "Unknown")),
            "year": str(item.get("year", "Unknown")),
            "document_type": str(item.get("document_type", "standard")),
            "category": str(item.get("category", "general")),
            "page": int(item.get("page", 1)),
            "page_end": int(item.get("page_end", 1)),
            "section": str(item.get("section", "General")),
            "official_url": str(item.get("official_url", "")),
            "provenance": f"{item.get('source_title', doc_name)}, p. {item.get('page', 1)}",
            "text": item.get("text", "")
        }
        metadata_list.append(meta)

    emb_matrix = np.array(embeddings_list, dtype=np.float32)
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized_matrix = emb_matrix / norms

    np.save(NPY_OUT, normalized_matrix)
    with open(META_OUT, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)
    print(f"Successfully exported {len(metadata_list)} chunks to {META_OUT} and matrix shape {normalized_matrix.shape} to {NPY_OUT}")

if __name__ == "__main__":
    run_export()
