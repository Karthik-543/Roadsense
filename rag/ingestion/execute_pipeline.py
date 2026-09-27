import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    import ingestion.extract_pdf
    import ingestion.chunk_text
    import ingestion.create_embeddings
    import ingestion.build_vectorstore
