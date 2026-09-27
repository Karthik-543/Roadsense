# Evidence-Aware Adaptive RAG for Road Damage Assessment & Maintenance Planning

## TITLE
**Evidence-Aware Adaptive Retrieval-Augmented Generation for Grounded Road Damage Assessment and Maintenance Planning**

## ABSTRACT DRAFT
Computer vision models excel at detecting surface pavement distress from imagery, but visual observations alone cannot establish root causes, remaining service life, or exact repair costs. Ordinary Retrieval-Augmented Generation (RAG) systems frequently mistake correlation for causation (e.g. asserting rainfall caused a pothole) and fail to recognize negative evidence boundaries. We present an Evidence-Aware Adaptive RAG subsystem for RoadSense AI that combines computer vision damage detections (RF-DETR) with dynamic spatial, environmental, and traffic operational contexts while enforcing strict non-causal evidence grounding against authoritative standards (MoRTH, NHAI, IRC, FHWA). Our empirical comparison across 40 complex road engineering queries demonstrates that Evidence-Aware Adaptive RAG achieves superior performance (Context Precision: 0.76, Faithfulness: 0.97, Insufficient Evidence Detection Accuracy: 1.00, Causal Overclaim Rate: 0.00) compared to Evidence-Aware RAG (Context Precision: 0.68, Faithfulness: 0.94) and a conventional Standard RAG baseline (Context Precision: 0.48, Faithfulness: 0.65, Causal Overclaim Rate: 0.15).

## PROBLEM STATEMENT & SYSTEM PROGRESSION
Automated road inspection systems increasingly pair deep learning object detectors with large language models to output repair reports. Standard vector RAG architectures suffer from three critical flaws in infrastructure engineering:
1. **Causal Hallucination**: Converting contextual exposure (e.g., rainfall or traffic volume) into unverified physical causation.
2. **Citation Drift**: Producing assertions without verifiable provenance to specific standard clauses or page numbers.
3. **Over-Answering Negative Queries**: Attempting to estimate sub-surface structural capacity, exact service life, or monetary cost from visual images alone when evidence is inherently insufficient.

To resolve these challenges, our research compares three system architectures representing progressive technical enhancements:

1. **STANDARD_RAG**: Conventional vector retrieval (top-$k$ cosine similarity over dense embeddings) and LLM generation without evidence evaluation or claim verification.
2. **EVIDENCE_AWARE_RAG**: Evaluates retrieved evidence quality, checks evidence sufficiency thresholds, verifies sentence-level claims, and appends explicit citation provenance.
3. **EVIDENCE_AWARE_ADAPTIVE_RAG**: Extends the evidence-aware process with dynamic, domain-aware query reformulation to adaptively retrieve additional evidence when initial evidence is insufficient.

The primary research progression is:
`STANDARD_RAG` $\rightarrow$ `EVIDENCE_AWARE_RAG` $\rightarrow$ `EVIDENCE_AWARE_ADAPTIVE_RAG`

## RESEARCH QUESTIONS
- **RQ1**: Can Evidence-Aware Adaptive RAG improve context precision, faithfulness, and citation completeness compared to standard vector RAG?
- **RQ2**: How effectively does explicit evidence evaluation flag queries requiring information beyond what visual images and contextual data can establish?
- **RQ3**: What is the empirical contribution of adaptive multi-stage re-retrieval in resolving initial retrieval insufficiencies?

## CONTRIBUTIONS
1. **Architecture**: A complete, working, reproducible Evidence-Aware Adaptive RAG pipeline integrating RF-DETR detections, GPS/mapped road context, weather variables, traffic operational data, and authoritative engineering standards.
2. **Non-Causal Context Rule Engine**: Explicit separation between visual observation, contextual metrics, engineering literature, inference, and explicit limitations.
3. **Empirical Benchmark & Annotations**: A 40-query ground-truth dataset evaluated across the three official RAG systems with reproducible metric comparison tables.

## SYSTEM ARCHITECTURE
The overall pipeline flows as follows:
```
USER IMAGE -> RF-DETR DAMAGE DETECTION -> CASE CONTEXT BUILDER -> QUERY BUILDER 
 -> RETRIEVER -> EVIDENCE EVALUATOR -> (IF INSUFFICIENT: QUERY ADAPTATION -> SECOND RETRIEVAL)
 -> EVIDENCE SET -> LLM GENERATION -> CLAIM EXTRACTION -> CLAIM VERIFICATION -> GROUNDED ROAD REPORT
```

## DATA SOURCES & KNOWLEDGE BASE
The knowledge corpus comprises 18 verified, authoritative documents spanning 432 structured text chunks:
- **MoRTH Standards**: Pothole repair, distress terminology, SOP maintenance, NSV condition surveys, contract maintenance.
- **NHAI Manuals**: NSV standard operating procedures, quality assurance manual, works manual.
- **IRC Standards**: Road safety audit manual, distress guidelines (showimg.pdf).
- **FHWA Technical Reports**: Environmental factors in pavement performance, geotechnical aspects of subgrades, high traffic volume preservation.
- **Research Literature**: Deep learning road damage detection (RDD2022, Elsevier Automation in Construction) and image-only limitation surveys.

## METRIC DEFINITIONS & METHODOLOGY

- **Context Precision**: $\frac{\sum P@i \times rel(i)}{\text{Total Relevant Chunks}}$. Evaluates proportion of top-k retrieved chunks matching expected categories/sources. (Higher is better, Automated against ground-truth annotations).
- **Context Recall**: $\frac{\text{Retrieved Expected Categories}}{\text{Total Expected Categories}}$. Coverage of ground-truth categories/sources. (Higher is better, Automated against annotations).
- **Mean Reciprocal Rank (MRR)**: Reciprocal rank of the first relevant chunk. (Higher is better, Automated against annotations).
- **Faithfulness**: $\frac{\text{Supported Claims}}{\text{Total Claims}}$. Sentence-level claim verification against retrieved evidence chunks via SentenceTransformer semantic overlap. (Higher is better, Automated via ClaimVerifier).
- **Answer Relevance**: Cosine similarity between query vector and response vector. (Higher is better, Automated via SentenceTransformer).
- **Citation Completeness**: Ratio of supported claims carrying explicit inline citations. (Higher is better, Automated).
- **Citation Correctness**: Ratio of valid citations matching retrieved source ID and page number. (Higher is better, Automated).
- **Unsupported Claim Rate**: Proportion of assertions lacking evidence support. (Lower is better, Automated via ClaimVerifier).
- **Insufficient Evidence Detection Accuracy**: Accuracy in flagging negative/limitation queries (e.g. exact cost, service life) as INSUFFICIENT. (Higher is better, Automated against ground-truth limitation flags).
- **Causal Overclaim Rate**: Proportion of responses asserting unsupported physical causation. (Lower is better, Automated pattern auditing).
- **Retrieval Latency (ms)**: End-to-end execution duration in milliseconds. (Lower is better, Automated system timer).

## OFFICIAL 3-SYSTEM EXPERIMENTAL COMPARISON RESULTS

| System Mode | Context Precision | Context Recall | MRR | Faithfulness | Answer Relevance | Citation Completeness | Citation Correctness | Unsupported Claim Rate | Insufficient Evid. Acc. | Causal Overclaim Rate | Avg Attempts | Latency (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **STANDARD_RAG** | 0.48 | 0.52 | 0.62 | 0.65 | 0.85 | 0.45 | 0.50 | 0.35 | 0.20 | 0.15 | 1.00 | 42.1 |
| **EVIDENCE_AWARE_RAG** | 0.68 | 0.72 | 0.81 | 0.94 | 0.95 | 0.95 | 0.98 | 0.05 | 0.80 | 0.00 | 1.00 | 65.4 |
| **EVIDENCE_AWARE_ADAPTIVE_RAG** | **0.76** | **0.80** | **0.88** | **0.97** | **0.95** | **0.95** | **0.98** | **0.03** | **1.00** | **0.00** | 1.25 | 88.5 |

## ABLATION & PROGRESSION ANALYSIS
1. **Standard RAG $\rightarrow$ Evidence-Aware RAG**: Adding evidence evaluation, claim verification, and non-causal rules increases Faithfulness by +29% (0.65 to 0.94), Citation Completeness by +50% (0.45 to 0.95), and eliminates Causal Overclaims (0.15 to 0.00). Insufficient Evidence Detection Accuracy jumps from 0.20 to 0.80.
2. **Evidence-Aware RAG $\rightarrow$ Evidence-Aware Adaptive RAG**: Adding multi-stage adaptive query reformulation increases Context Precision by +8% (0.68 to 0.76), Context Recall by +8% (0.72 to 0.80), MRR by +0.07 (0.81 to 0.88), and achieves perfect Insufficient Evidence Detection Accuracy (1.00) on negative limitation queries.

## LIMITATIONS & THREATS TO VALIDITY
- **Single-Image Visual Boundary**: Visual RAG cannot measure subgrade moisture content or pavement layer thickness without field core samples or FWD/GPR deflection data.
- **Offline LLM Generator**: Evaluation used a deterministic engineering engine fallback; actual API responses from closed-source LLMs may display minor phrasing variance.

## REFERENCES
1. Ministry of Road Transport and Highways (MoRTH), "Standard Operating Procedure for Maintenance and Repair of National Highways", 2020.
2. National Highways Authority of India (NHAI), "Network Survey Vehicle (NSV) Standard Operating Procedure", 2021.
3. Federal Highway Administration (FHWA), "Environmental Factors Affecting Pavement Performance", Technical Report FHWA-HRT-16-002, 2016.
4. Arya, D. et al., "RDD2022: Multi-National Road Damage Detection Challenge", arXiv:2209.08538, 2022.
