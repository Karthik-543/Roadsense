import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

INPUT_DIR = Path("data/processed/chunks")
OUTPUT_FILE = Path("data/processed/embeddings.json")

model_name = "all-MiniLM-L6-v2"
print(f"Loading embedding model: {model_name}...")
model = SentenceTransformer(model_name)

documents = []

for file in INPUT_DIR.glob("*_chunks.json"):
    chunks = json.loads(file.read_text(encoding="utf-8"))
    for chunk in chunks:
        documents.append(chunk)

print(f"Total chunks loaded: {len(documents)}")

texts = [doc["text"] for doc in documents]

print("Computing sentence embeddings...")
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True
)

for doc, embedding in zip(documents, embeddings):
    doc["embedding"] = embedding.tolist()

OUTPUT_FILE.write_text(
    json.dumps(documents, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Successfully generated embeddings for {len(documents)} chunks.")
print(f"Saved to: {OUTPUT_FILE}")