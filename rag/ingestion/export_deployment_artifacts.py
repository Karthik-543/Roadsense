import os
import json
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_EMBEDDINGS = BASE_DIR / "data" / "processed" / "embeddings.json"
DEPLOYMENT_DIR = BASE_DIR / "data" / "deployment"
DEPLOYMENT_DIR.mkdir(parents=True, exist_ok=True)

NPY_OUT = DEPLOYMENT_DIR / "embeddings.npy"
META_OUT = DEPLOYMENT_DIR / "chunks_metadata.json"
CACHE_OUT = DEPLOYMENT_DIR / "query_cache.json"

STANDARD_QUERIES = [
    "What maintenance treatment and operational planning is required for the observed distress?",
    "What maintenance treatment is recommended for potholes?",
    "What standard repair procedure applies to severe alligator cracking?",
    "How does 20mm rainfall impact structural degradation of potholes?",
    "When should a road defect require full-depth patching vs cold mix?",
    "What safety protocols apply to highway lane closures during crack sealing?",
    "What repair procedure applies to longitudinal cracking?",
    "What repair procedure applies to transverse cracking?",
    "How does high traffic volume affect maintenance priority?",
    "What drainage inspections are required for flexible pavements?",
    "What quality assurance guidelines apply to bituminuous patching?",
    "What pavement condition parameters are measured by Network Survey Vehicles (NSV)?",
    "What are the MoRTH guidelines for pothole repair?",
    "What are the NHAI quality assurance standards for road maintenance?",
]

def export_artifacts():
    print(f"Reading embeddings from {INPUT_EMBEDDINGS}...")
    if not INPUT_EMBEDDINGS.exists():
        raise FileNotFoundError(f"Source embeddings file not found at {INPUT_EMBEDDINGS}")

    with open(INPUT_EMBEDDINGS, "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings_list = []
    metadata_list = []

    for idx, item in enumerate(data):
        emb = item.get("embedding")
        if not emb or len(emb) != 384:
            raise ValueError(f"Invalid embedding dimensions at index {idx}")
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
    print(f"Saved normalized embeddings matrix of shape {normalized_matrix.shape} to {NPY_OUT}")

    with open(META_OUT, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(metadata_list)} chunk metadata records to {META_OUT}")

    # Build query vector cache for standard queries using local SentenceTransformer if available
    build_query_cache()

    # Export ONNX model for arbitrary new user queries
    export_onnx_model(DEPLOYMENT_DIR)

def build_query_cache():
    query_cache = {}
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Generating precomputed query vector cache...")
        for q in STANDARD_QUERIES:
            vec = model.encode(q, convert_to_numpy=True).tolist()
            query_cache[q.strip().lower()] = vec
        
        with open(CACHE_OUT, "w", encoding="utf-8") as f:
            json.dump(query_cache, f, indent=2)
        print(f"Saved precomputed query vector cache ({len(query_cache)} entries) to {CACHE_OUT}")
    except Exception as e:
        print(f"Notice: Query cache generation skipped or partial: {e}")

def export_onnx_model(output_dir: Path):
    model_path = output_dir / "model.onnx"
    tokenizer_dir = output_dir / "tokenizer"
    tokenizer_dir.mkdir(parents=True, exist_ok=True)

    if model_path.exists() and (tokenizer_dir / "tokenizer.json").exists():
        print(f"ONNX model and tokenizer already exist at {model_path}")
        return

    print("Attempting ONNX export for all-MiniLM-L6-v2...")
    try:
        import torch
        from transformers import AutoTokenizer, AutoModel

        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        model.eval()

        tokenizer.save_pretrained(str(tokenizer_dir))

        dummy_text = "What is the maintenance treatment for potholes?"
        inputs = tokenizer(dummy_text, return_tensors="pt", padding=True, truncation=True)

        torch.onnx.export(
            model,
            (inputs["input_ids"], inputs["attention_mask"], inputs["token_type_ids"]),
            str(model_path),
            input_names=["input_ids", "attention_mask", "token_type_ids"],
            output_names=["last_hidden_state"],
            dynamic_axes={
                "input_ids": {0: "batch_size", 1: "sequence"},
                "attention_mask": {0: "batch_size", 1: "sequence"},
                "token_type_ids": {0: "batch_size", 1: "sequence"},
                "last_hidden_state": {0: "batch_size", 1: "sequence"}
            },
            opset_version=14
        )
        print(f"Successfully exported ONNX query encoder model to {model_path}")
    except Exception as err:
        print(f"Could not export ONNX model automatically: {err}")

if __name__ == "__main__":
    export_artifacts()
