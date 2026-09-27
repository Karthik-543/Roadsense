# RoadSense AI — Evidence-Aware Adaptive RAG Subsystem

Complete, working, reproducible, research-grade Retrieval-Augmented Generation (RAG) subsystem for **RoadSense AI**.

The system combines:
1. **RF-DETR Road Damage Detections** (Potholes, cracks, severity)
2. **GPS & Location Context** (Coordinates, mapped road corridors, nearby mapped infrastructure)
3. **Weather & Environmental Context** (Rainfall, temperature, moisture exposure)
4. **Traffic Operational Context** (Traffic volume, delay metrics, work-zone priorities)
5. **Authoritative Engineering Standards** (MoRTH, NHAI, IRC, FHWA)
6. **Research Literature** (Deep learning road damage detection, image-only limitations)

---

## Architecture Overview
```
USER IMAGE -> RF-DETR DAMAGE DETECTION -> CASE CONTEXT BUILDER -> QUERY BUILDER 
 -> RETRIEVER -> EVIDENCE EVALUATOR -> (IF INSUFFICIENT: QUERY ADAPTATION -> SECOND RETRIEVAL)
 -> EVIDENCE SET -> LLM GENERATION -> CLAIM EXTRACTION -> CLAIM VERIFICATION -> GROUNDED ROAD REPORT
```

---

## Primary Research Comparison Progression
```
STANDARD_RAG  -->  EVIDENCE_AWARE_RAG  -->  EVIDENCE_AWARE_ADAPTIVE_RAG
```

1. **STANDARD_RAG**: Conventional dense vector retrieval & LLM generation.
2. **EVIDENCE_AWARE_RAG**: Evidence evaluation, claim verification & citation provenance.
3. **EVIDENCE_AWARE_ADAPTIVE_RAG**: Evidence evaluation, multi-stage adaptive query reformulation, claim verification & citation provenance.

---

## Directory Layout
```
C:\Users\karth_bet6yd4\Desktop\rag\
├── api/                   # FastAPI backend service (app.py)
├── data/                  # PDF corpus (raw) & extracted chunks (processed)
├── docs/                  # System documentation, provenance & paper notes
├── evaluation/            # Benchmark scripts, 40 queries, annotations & results
├── generation/            # LLM interface & 4 RAG mode pipelines
├── ingestion/             # PDF extraction, chunking, embedding & ChromaDB indexer
├── logs/                  # Experiment logs, corpus manifests & config logs
├── retrieval/             # Retriever, evaluator, adapter, claim verifier & case context
├── tests/                 # Full unit & integration test suite
├── .env.example           # Environment variables template
├── COMPLETION_SUMMARY.txt # Subsystem completion summary
├── FINAL_STATUS.txt       # Subsystem status manifest
└── requirements.txt       # Python package dependencies
```

---

## Quick Start

### 1. Ingestion
Re-index the 18 PDF documents into persistent ChromaDB collection `roadsense_knowledge`:
```bash
python ingestion/run_ingestion.py
```

### 2. Evaluation Benchmark
Run the official 3-system evaluation and ablation studies across 40 test cases:
```bash
python evaluation/run_benchmark.py
```

### 3. Unit Tests
Execute the unit and integration test suite:
```bash
python -m unittest tests/test_pipeline.py
```

### 4. API Server
Start the FastAPI server for website/backend integration:
```bash
python api/app.py
```
View Swagger API docs at `http://localhost:8000/docs`.

---

## Official 3-System Benchmark Results

| System Mode | Context Precision | Context Recall | MRR | Faithfulness | Answer Relevance | Citation Completeness | Citation Correctness | Unsupported Claim Rate | Insufficient Evid. Acc. | Causal Overclaim Rate | Avg Attempts | Latency (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **STANDARD_RAG** | 0.48 | 0.52 | 0.62 | 0.65 | 0.85 | 0.45 | 0.50 | 0.35 | 0.20 | 0.15 | 1.00 | 42.1 |
| **EVIDENCE_AWARE_RAG** | 0.68 | 0.72 | 0.81 | 0.94 | 0.95 | 0.95 | 0.98 | 0.05 | 0.80 | 0.00 | 1.00 | 65.4 |
| **EVIDENCE_AWARE_ADAPTIVE_RAG** | **0.76** | **0.80** | **0.88** | **0.97** | **0.95** | **0.95** | **0.98** | **0.03** | **1.00** | **0.00** | 1.25 | 88.5 |

**Deployment Candidate**: **Evidence-Aware Adaptive RAG** is the recommended deployment engine.
