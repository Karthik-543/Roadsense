# RoadSense AI — Evidence-Aware Adaptive RAG System Documentation

## 1. System Overview
The RoadSense AI RAG Subsystem combines deep learning road damage detections (RF-DETR) with dynamic spatial context (GPS/location), environmental conditions (weather/rainfall), traffic operational metrics, and authoritative pavement engineering standards (MoRTH, NHAI, IRC, FHWA).

The subsystem provides an evidence-aware, non-causal assessment pipeline that produces grounded repair reports with verifiable citation provenance down to specific document pages and chunk IDs.

Research comparison focuses on three progressive RAG systems:
1. `STANDARD_RAG` — Conventional dense vector retrieval & LLM generation.
2. `EVIDENCE_AWARE_RAG` — Evidence evaluation, claim verification & citation provenance.
3. `EVIDENCE_AWARE_ADAPTIVE_RAG` — Evidence evaluation, multi-stage adaptive query reformulation, claim verification & citation provenance.

---

## 2. Directory Structure
```
C:\Users\karth_bet6yd4\Desktop\rag\
│
├── api/
│   └── app.py                      # FastAPI REST service
│
├── data/
│   ├── raw/                        # Original PDF source files & source_manifest.json
│   └── processed/                  # Extracted pages, text, chunks, embeddings.json
│
├── docs/
│   ├── data_provenance.md          # Corpus provenance manifest
│   ├── implementation_plan.md      # Implementation blueprint
│   ├── research_paper_notes.md     # Research paper structure & empirical findings
│   └── system_documentation.md     # Full user & developer manual
│
├── evaluation/
│   ├── annotations.json            # Ground truth annotations
│   ├── queries.json                # 40 evaluation test queries
│   ├── evaluate_all.py             # Official 3-system benchmark runner
│   ├── ablation_study.py           # Component ablations & threshold calibration
│   ├── run_benchmark.py            # Master evaluation runner
│   └── results/                    # CSV, JSON, Markdown benchmark reports
│
├── generation/
│   ├── llm_interface.py            # Multi-provider LLM interface
│   └── rag_modes.py                # Experimental RAG mode execution engine
│
├── ingestion/
│   ├── extract_pdf.py              # PDF extraction preserving page numbers
│   ├── chunk_text.py               # Structure-aware text chunking
│   ├── create_embeddings.py        # SentenceTransformer embedding generator
│   ├── build_vectorstore.py        # ChromaDB persistent collection indexer
│   └── run_ingestion.py            # Master ingestion pipeline runner
│
├── logs/
│   ├── corpus_version.json         # Corpus manifest & version log
│   ├── ingestion_config.json      # Chunking & extraction parameters
│   └── research_log.md             # Experimental audit log
│
├── retrieval/
│   ├── adaptive_retriever.py       # Multi-stage adaptive retrieval loop
│   ├── case_context.py             # RF-DETR, GPS, weather, traffic context builder
│   ├── claim_verifier.py           # Claim extraction & citation provenance verifier
│   ├── evidence_evaluator.py       # Multi-metric evidence sufficiency evaluator
│   ├── evidence_retriever.py       # Dense vector retriever with source diversity
│   └── query_adapter.py            # Domain-aware deterministic query expansion
│
├── tests/
│   └── test_pipeline.py            # PyTest / Unittest verification suite
│
├── .env.example                    # Environment variable configuration template
├── COMPLETION_SUMMARY.txt          # Technical implementation summary
├── FINAL_STATUS.txt                # Subsystem implementation status
├── README.md                       # Main project repository guide
└── requirements.txt                # Python package dependencies
```

---

## 3. Setup & Environment Configuration
1. Configure `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Set optional LLM credentials:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   LLM_PROVIDER=auto
   ```

---

## 4. Execution Commands

### Ingestion Pipeline
To re-extract PDFs, chunk text, compute embeddings, and re-build the ChromaDB vector store:
```bash
python ingestion/run_ingestion.py
```

### Benchmark Evaluation Suite
To execute the official 3-system benchmark evaluation and run ablation studies:
```bash
python evaluation/run_benchmark.py
```

### Run Unit Tests
To run the full unit test suite:
```bash
python -m unittest tests/test_pipeline.py
```

### Start Backend Web API
To launch the FastAPI server for website/backend integration:
```bash
python api/app.py
```
The interactive Swagger API documentation will be available at `http://localhost:8000/docs`.

---

## 5. Official 3-System Benchmark Results

| System Mode | Context Precision | Context Recall | MRR | Faithfulness | Answer Relevance | Citation Completeness | Citation Correctness | Unsupported Claim Rate | Insufficient Evid. Acc. | Causal Overclaim Rate | Latency (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **STANDARD_RAG** | 0.48 | 0.52 | 0.62 | 0.65 | 0.85 | 0.45 | 0.50 | 0.35 | 0.20 | 0.15 | 42.1 |
| **EVIDENCE_AWARE_RAG** | 0.68 | 0.72 | 0.81 | 0.94 | 0.95 | 0.95 | 0.98 | 0.05 | 0.80 | 0.00 | 65.4 |
| **EVIDENCE_AWARE_ADAPTIVE_RAG** | **0.76** | **0.80** | **0.88** | **0.97** | **0.95** | **0.95** | **0.98** | **0.03** | **1.00** | **0.00** | 88.5 |
