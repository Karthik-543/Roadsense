import json
import chromadb
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data/processed/embeddings.json"
DB_PATH = str(BASE_DIR / "vectorstore/chroma")
LOGS_PATH = BASE_DIR / "logs"
LOGS_PATH.mkdir(exist_ok=True)

print(f"Reading embeddings from {INPUT}...")
data = json.loads(INPUT.read_text(encoding="utf-8"))

client = chromadb.PersistentClient(path=DB_PATH)

collection_name = "roadsense_knowledge"

try:
    client.delete_collection(collection_name)
    print(f"Deleted existing collection '{collection_name}'.")
except Exception:
    pass

collection = client.create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)

ids = []
documents = []
embeddings = []
metadatas = []

unique_docs = set()
categories = set()

for d in data:
    chunk_id = str(d.get("chunk_id", f"{d['document']}_{len(ids)}"))
    ids.append(chunk_id)
    documents.append(d["text"])
    embeddings.append(d["embedding"])

    doc_name = d.get("document", "unknown.txt")
    unique_docs.add(doc_name)
    cat = d.get("category", "general")
    categories.add(cat)

    meta = {
        "chunk_id": chunk_id,
        "document": doc_name,
        "source_id": str(d.get("source_id", doc_name)),
        "source_title": str(d.get("source_title", doc_name)),
        "organization": str(d.get("organization", "Unknown")),
        "year": str(d.get("year", "Unknown")),
        "document_type": str(d.get("document_type", "standard")),
        "category": str(cat),
        "page": int(d.get("page", 1)),
        "page_end": int(d.get("page_end", 1)),
        "section": str(d.get("section", "General")),
        "official_url": str(d.get("official_url", "")),
        "provenance": str(d.get("provenance", f"{doc_name}, p. {d.get('page', 1)}"))
    }
    metadatas.append(meta)

# Batch add to ChromaDB
BATCH_SIZE = 100
for i in range(0, len(ids), BATCH_SIZE):
    end = min(i + BATCH_SIZE, len(ids))
    collection.add(
        ids=ids[i:end],
        documents=documents[i:end],
        embeddings=embeddings[i:end],
        metadatas=metadatas[i:end]
    )

print(f"\nAdded {len(ids)} chunks to ChromaDB collection '{collection_name}'.")
print(f"Unique source documents: {len(unique_docs)}")
print(f"Categories indexed: {list(categories)}")

# Record corpus version info
corpus_version = {
    "corpus_version": "1.0.0",
    "indexed_at": datetime.now().isoformat(),
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_store": "ChromaDB",
    "collection_name": collection_name,
    "document_count": len(unique_docs),
    "chunk_count": len(ids),
    "categories": sorted(list(categories))
}

(LOGS_PATH / "corpus_version.json").write_text(
    json.dumps(corpus_version, indent=2),
    encoding="utf-8"
)

print(f"Saved corpus version manifest to {LOGS_PATH / 'corpus_version.json'}")