import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    print("=" * 60)
    print("ROADSENSE AI — RAG KNOWLEDGE BASE INGESTION PIPELINE")
    print("=" * 60)

    # 1. PDF Extraction
    print("\n[STEP 1/4] Extracting text from PDFs...")
    import ingestion.extract_pdf

    # 2. Chunking
    print("\n[STEP 2/4] Chunking structured text...")
    import ingestion.chunk_text

    # 3. Embedding Generation
    print("\n[STEP 3/4] Generating sentence embeddings...")
    import ingestion.create_embeddings

    # 4. Vectorstore Indexing
    print("\n[STEP 4/4] Indexing chunks into ChromaDB...")
    import ingestion.build_vectorstore

    print("\n" + "=" * 60)
    print("INGESTION PIPELINE COMPLETED SUCCESSFULLY.")
    print("=" * 60)

if __name__ == "__main__":
    main()
