# Evidence-Aware Adaptive RAG Subsystem for RoadSense AI

Build a complete, reproducible, evidence-aware adaptive RAG subsystem for RoadSense AI inside `C:\Users\karth_bet6yd4\Desktop\rag`. The system will support evidence-grounded road damage assessments incorporating RF-DETR detection evidence, location/GPS context, weather engineering context, traffic operational context, multi-stage adaptive retrieval, claim extraction & verification, citation provenance tracking, and a comparative evaluation framework across four experimental modes.

---

## User Review Required

> [!IMPORTANT]
> **Execution Environment Note**: Command execution tools in this environment hit Windows path permission restrictions when modifying system directories (`.gemini`). All pipeline stages (ingestion, vectorstore indexing, adaptive retrieval, claim verification, evaluation benchmark, API server, and test suites) will be implemented as self-executing Python scripts and modular packages that can be executed directly via Python in your terminal environment.

> [!NOTE]
> **LLM Provider Strategy**: The system implements an abstract `LLMInterface` supporting OpenAI (`gpt-4o`/`gpt-4o-mini`), local transformer models via Hugging Face/Ollama, as well as a deterministic engineering fallback generator when external API keys are omitted. This guarantees offline operation and reproducible metric calculation without hard-coded API dependencies.

---

## Open Questions

1. **Embedding Model Baseline**: The current codebase uses `all-MiniLM-L6-v2`. Would you like to evaluate an additional embedding model (e.g. `bge-small-en-v1.5`) as part of the embedding ablation study?
2. **Evaluation Query Expansion**: The baseline currently has 20 queries (`queries.json`). We plan to expand this to 35-50 queries covering complex multi-evidence, weather-pavement interactions, traffic maintenance constraints, and explicit negative evidence limits (e.g., service life, repair cost, structural capacity). Are there any specific road damage classes or IRC/MoRTH standards you want emphasized?

---

## Proposed Changes

---

### 1. Ingestion & Provenance Subsystem (`ingestion/` & `data/`)

#### [NEW] [source_manifest.json](file:///C:/Users/karth_bet6yd4/Desktop/rag/data/raw/source_manifest.json)
- Create authoritative source provenance tracking file mapping every PDF and context document to title, organization, year, document type, official URL, local path, and access status.

#### [MODIFY] [extract_pdf.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/ingestion/extract_pdf.py)
- Upgrade PDF extractor to extract structured text with page-level metadata preservation (`page_number`, `document_type`, `section_headers`).

#### [MODIFY] [chunk_text.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/ingestion/chunk_text.py)
- Implement structure-aware chunking preserving headings, paragraphs, and page boundaries, writing chunk metadata (`chunk_id`, `page`, `source_id`, `section`).

#### [MODIFY] [create_embeddings.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/ingestion/create_embeddings.py)
- Generate embedding vectors using `all-MiniLM-L6-v2` with batching, preserving metadata attributes per chunk.

#### [MODIFY] [build_vectorstore.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/ingestion/build_vectorstore.py)
- Index chunks into persistent ChromaDB collection `roadsense_knowledge` with rich metadata filtering capabilities. Output `logs/corpus_version.json` and `logs/ingestion_config.json`.

---

### 2. Case Context & Retrieval Subsystem (`retrieval/`)

#### [NEW] [case_context.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/retrieval/case_context.py)
- Build case context payload handlers combining RF-DETR damage detection outputs, GPS location/mapped road context, dynamic weather inputs, and traffic operational data. Ensure raw values are preserved without invalid causal conversions.

#### [MODIFY] [evidence_retriever.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/retrieval/evidence_retriever.py)
- Implement dense vector retrieval supporting top-$k$ tuning ($k \in \{3, 5, 8, 10\}$), similarity scoring, metadata filtering, and source-aware diversity retrieval.

#### [MODIFY] [evidence_evaluator.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/retrieval/evidence_evaluator.py)
- Implement `evaluate_evidence()` with multi-metric assessment: top score, mean score, strong hit count, source diversity, claim specificity, and evidence support status (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `INSUFFICIENT`, `CONFLICTING`).

#### [MODIFY] [query_adapter.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/retrieval/query_adapter.py)
- Build domain-aware query adaptation logic for distress types (potholes, longitudinal/transverse/alligator cracking), environmental moisture/temperature, traffic volume, and road classification.

#### [MODIFY] [adaptive_retriever.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/retrieval/adaptive_retriever.py)
- Implement `adaptive_retrieve()` execution loop: initial retrieval $\rightarrow$ evaluation $\rightarrow$ query adaptation $\rightarrow$ second retrieval $\rightarrow$ evidence comparison and merged evidence output.

#### [NEW] [claim_verifier.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/retrieval/claim_verifier.py)
- Implement claim extraction and verification pipeline: classify claims into `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `NOT_VERIFIABLE`, prune/rewrite unsupported claims, and append citation provenance (`[Source: title, p. XX, chunk_id]`).

---

### 3. Generation, RAG Modes & API (`generation/` & `api/`)

#### [NEW] [llm_interface.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/generation/llm_interface.py)
- Configurable LLM abstraction layer supporting OpenAI API, local transformers, and deterministic evidence-grounded engineering generator.

#### [NEW] [rag_modes.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/generation/rag_modes.py)
- Implement four distinct operational modes for reproducible comparison:
  - **Mode A**: `NO_RAG` (LLM Baseline)
  - **Mode B**: `STANDARD_RAG` (Top-$k$ Vector Retrieval + LLM)
  - **Mode C**: `EVIDENCE_AWARE_RAG` (Retrieval + Evidence Evaluation + Claim Verification)
  - **Mode D**: `EVIDENCE_AWARE_ADAPTIVE_RAG` (Retrieval + Evidence Evaluation + Adaptive Re-retrieval + Claim Verification + Citation Provenance)

#### [NEW] [app.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/api/app.py)
- FastAPI service providing `POST /api/v1/road-assessment`, `GET /api/v1/health`, `GET /api/v1/config`. Handles missing weather/traffic/GPS gracefully without fabricating data.

---

### 4. Evaluation Benchmark, Ablation & Documentation (`evaluation/`, `docs/`, `logs/`)

#### [MODIFY] [queries.json](file:///C:/Users/karth_bet6yd4/Desktop/rag/evaluation/queries.json)
- Expand evaluation query set to 35-50 test cases across direct, related, specific, synthesis, insufficient-evidence, multi-evidence, weather-pavement, and traffic-operational categories.

#### [NEW] [annotations.json](file:///C:/Users/karth_bet6yd4/Desktop/rag/evaluation/annotations.json)
- Create ground-truth annotation dataset specifying expected evidence types, sufficiency criteria, relevant document IDs, and negative evidence limits.

#### [NEW] [evaluate_all.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/evaluation/evaluate_all.py)
- Automated evaluation script running Modes A, B, C, D across identical query sets. Calculates retrieval metrics (Context Precision, Recall, MRR, nDCG) and generation/RoadSense metrics (Faithfulness, Relevance, Citation Coverage/Correctness, Unsupported Claim Rate, Insufficient Evidence Accuracy, Causal Overclaim Rate).

#### [NEW] [ablation_study.py](file:///C:/Users/karth_bet6yd4/Desktop/rag/evaluation/ablation_study.py)
- Run ablation experiments across dense-only, dense+expansion, evaluator-only, adaptive-only, and verification-only configurations. Perform threshold calibration (0.40-0.70).

#### [NEW] [research_log.md](file:///C:/Users/karth_bet6yd4/Desktop/rag/logs/research_log.md)
- Maintain structured log of experiments, corpus versions, model configs, metric outputs, and research conclusions.

#### [NEW] [research_paper_notes.md](file:///C:/Users/karth_bet6yd4/Desktop/rag/docs/research_paper_notes.md)
- Complete research paper structure containing abstract, problem statement, architecture, methodology, empirical results table, ablation analysis, limitations, and future work.

#### [NEW] [system_documentation.md](file:///C:/Users/karth_bet6yd4/Desktop/rag/docs/system_documentation.md) & [data_provenance.md](file:///C:/Users/karth_bet6yd4/Desktop/rag/docs/data_provenance.md)
- System user manual, backend integration specs, and data provenance manifest.

#### [NEW] [FINAL_STATUS.txt](file:///C:/Users/karth_bet6yd4/Desktop/rag/FINAL_STATUS.txt) & [COMPLETION_SUMMARY.txt](file:///C:/Users/karth_bet6yd4/Desktop/rag/COMPLETION_SUMMARY.txt)
- Implementation status summary, metric comparison table, deployment recommendations based on empirical results, and exact run instructions.

---

## Verification Plan

### Automated Verification
- **Pipeline Execution**: Run ingestion script `python ingestion/extract_pdf.py`, `python ingestion/chunk_text.py`, `python ingestion/create_embeddings.py`, `python ingestion/build_vectorstore.py`.
- **Smoke Tests**: Run unit & integration test suite verifying ingestion integrity, vector store querying, adaptive retrieval, claim verifier, and API endpoints.
- **Benchmark Suite**: Execute benchmark script to generate `final_comparison.json`, `final_comparison.csv`, and `final_comparison.md`.

### Manual Verification
- **API Payload Validation**: Test `POST /api/v1/road-assessment` with sample JSON payloads containing image damage detections, GPS, weather, and traffic context.
- **Citation Provenance Audit**: Verify that generated reports contain exact source title, page number, and chunk citations for all engineering claims, and that unverified/overclaimed statements are automatically pruned.
