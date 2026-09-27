import os
import sys

# Force lightweight deployment mode before any imports
os.environ["RAG_DEPLOYMENT_MODE"] = "lightweight"

def test_lightweight_startup_imports():
    """
    Verifies that importing api.app in lightweight deployment mode
    loads cleanly without importing heavy ML packages into sys.modules.
    """
    # Add rag directory to sys.path if not present
    rag_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if rag_dir not in sys.path:
        sys.path.insert(0, rag_dir)

    # Import the FastAPI application
    from api.app import app, pipeline

    forbidden_modules = [
        "torch",
        "sentence_transformers",
        "transformers",
        "chromadb",
        "huggingface_hub"
    ]

    loaded_forbidden = [mod for mod in forbidden_modules if mod in sys.modules]
    assert not loaded_forbidden, f"Forbidden heavy modules loaded in sys.modules during lightweight startup: {loaded_forbidden}"
    print("✓ Verification PASSED: Zero heavy modules loaded in sys.modules!")

    # Verify basic config route / pipeline initialization
    from retrieval.evidence_retriever import RAG_DEPLOYMENT_MODE
    assert RAG_DEPLOYMENT_MODE == "lightweight", f"Expected lightweight deployment mode, got {RAG_DEPLOYMENT_MODE}"
    print(f"✓ Verification PASSED: Deployment mode is '{RAG_DEPLOYMENT_MODE}'")

    # Execute a lightweight assessment test call
    res = pipeline.run_assessment(
        query="What maintenance treatment is recommended for potholes?",
        mode="EVIDENCE_AWARE_ADAPTIVE_RAG"
    )

    assert res["rag_mode"] == "EVIDENCE_AWARE_ADAPTIVE_RAG"
    assert "report" in res and len(res["report"]) > 0
    assert "evidence" in res
    print("✓ Verification PASSED: Pipeline ran assessment successfully in lightweight mode!")

if __name__ == "__main__":
    test_lightweight_startup_imports()
