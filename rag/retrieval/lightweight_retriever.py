import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DEPLOYMENT_DIR = BASE_DIR / "data" / "deployment"
NPY_PATH = DEPLOYMENT_DIR / "embeddings.npy"
META_PATH = DEPLOYMENT_DIR / "chunks_metadata.json"
CACHE_PATH = DEPLOYMENT_DIR / "query_cache.json"

class LightweightRetriever:
    """
    Lightweight, ultra-fast vector retriever running strictly in CPU memory.
    Uses precomputed normalized NumPy embeddings matrix, metadata JSON,
    and a hybrid query encoder (Precomputed Query Cache + ONNXRuntime CPU fallback).
    Requires NO PyTorch, NO CUDA, and NO ChromaDB at runtime.
    Memory Footprint: < 5 MB RAM (using query cache) to ~45 MB RAM (using ONNXRuntime CPU).
    """

    def __init__(self):
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.chunks_metadata: List[Dict[str, Any]] = []
        self.query_cache: Dict[str, List[float]] = {}
        self.session = None
        self.tokenizer = None
        self.encoder_type = None

        self._load_artifacts()
        self._init_encoder()

    def _load_artifacts(self):
        if NPY_PATH.exists() and META_PATH.exists():
            try:
                self.embeddings_matrix = np.load(NPY_PATH)
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self.chunks_metadata = json.load(f)
                print(f"[LightweightRetriever] Loaded {len(self.chunks_metadata)} chunks & matrix shape {self.embeddings_matrix.shape}")
            except Exception as e:
                print(f"[LightweightRetriever] Artifact load warning: {e}")
        else:
            print(f"[LightweightRetriever] Deployment artifacts not found at {DEPLOYMENT_DIR}")

        if CACHE_PATH.exists():
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    self.query_cache = json.load(f)
                print(f"[LightweightRetriever] Loaded {len(self.query_cache)} precomputed query vectors.")
            except Exception as e:
                print(f"[LightweightRetriever] Query cache warning: {e}")

    def _init_encoder(self):
        model_onnx = DEPLOYMENT_DIR / "model.onnx"
        tokenizer_dir = DEPLOYMENT_DIR / "tokenizer"

        # Try ONNX Runtime CPU Engine
        if model_onnx.exists() and tokenizer_dir.exists():
            try:
                import onnxruntime as ort
                from tokenizers import Tokenizer
                self.session = ort.InferenceSession(str(model_onnx), providers=["CPUExecutionProvider"])
                self.tokenizer = Tokenizer.from_file(str(tokenizer_dir / "tokenizer.json"))
                self.encoder_type = "onnx_tokenizers"
                print("[LightweightRetriever] Initialized ONNXRuntime + Tokenizers CPU engine.")
                return
            except Exception:
                try:
                    import onnxruntime as ort
                    from transformers import AutoTokenizer
                    self.session = ort.InferenceSession(str(model_onnx), providers=["CPUExecutionProvider"])
                    self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir))
                    self.encoder_type = "onnx_transformers"
                    print("[LightweightRetriever] Initialized ONNXRuntime + AutoTokenizer CPU engine.")
                    return
                except Exception as e:
                    print(f"[LightweightRetriever] ONNX init note: {e}")

        # Fallback to SentenceTransformer if installed (Research Mode)
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
            self.encoder_type = "sentence_transformers"
            print("[LightweightRetriever] Initialized SentenceTransformer query encoder.")
            return
        except Exception:
            pass

        self.encoder_type = "cache_or_keyword"
        print("[LightweightRetriever] Initialized Query Cache + Keyword fallback encoder.")

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encodes query string into L2-normalized 384-d vector.
        Uses exact precomputed query cache if available, or ONNX CPU inference.
        """
        normalized_q = query.strip().lower()

        # 1. Check Precomputed Query Cache (0ms, 0MB RAM)
        if normalized_q in self.query_cache:
            vec = np.array(self.query_cache[normalized_q], dtype=np.float32)
            norm = np.linalg.norm(vec)
            return vec / (norm if norm > 0 else 1.0)

        # Partial match in cache
        for cached_q, vec_list in self.query_cache.items():
            if cached_q in normalized_q or normalized_q in cached_q:
                vec = np.array(vec_list, dtype=np.float32)
                norm = np.linalg.norm(vec)
                return vec / (norm if norm > 0 else 1.0)

        # 2. ONNXRuntime Tokenizers CPU Inference (~40MB RAM)
        if self.encoder_type == "onnx_tokenizers" and self.session and self.tokenizer:
            try:
                encoded = self.tokenizer.encode(query)
                input_ids = np.array([encoded.ids], dtype=np.int64)
                attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
                token_type_ids = np.array([encoded.type_ids], dtype=np.int64)

                input_feed = {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "token_type_ids": token_type_ids
                }
                outputs = self.session.run(None, input_feed)
                last_hidden_state = outputs[0]
                mask = attention_mask[:, :, np.newaxis]
                sum_embeddings = np.sum(last_hidden_state * mask, axis=1)
                sum_mask = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
                mean_pooled = sum_embeddings / sum_mask
                norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
                norm[norm == 0] = 1.0
                return (mean_pooled / norm)[0]
            except Exception as e:
                print(f"[LightweightRetriever] ONNX tokenizers run error: {e}")

        elif self.encoder_type == "onnx_transformers" and self.session and self.tokenizer:
            try:
                inputs = self.tokenizer(query, return_tensors="np", padding=True, truncation=True)
                input_feed = {
                    "input_ids": inputs["input_ids"].astype(np.int64),
                    "attention_mask": inputs["attention_mask"].astype(np.int64),
                    "token_type_ids": inputs.get("token_type_ids", np.zeros_like(inputs["input_ids"])).astype(np.int64)
                }
                outputs = self.session.run(None, input_feed)
                last_hidden_state = outputs[0]
                mask = inputs["attention_mask"][:, :, np.newaxis]
                sum_embeddings = np.sum(last_hidden_state * mask, axis=1)
                sum_mask = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
                mean_pooled = sum_embeddings / sum_mask
                norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
                norm[norm == 0] = 1.0
                return (mean_pooled / norm)[0]
            except Exception as e:
                print(f"[LightweightRetriever] ONNX transformers run error: {e}")

        # 3. SentenceTransformer (Research Mode)
        if hasattr(self, "encoder") and self.encoder:
            vec = self.encoder.encode(query, convert_to_numpy=True)
            norm = np.linalg.norm(vec)
            return vec / (norm if norm > 0 else 1.0)

        # 4. Keyword similarity fallback if vector encoder fails
        query_words = set(normalized_q.split())
        scores = []
        for meta in self.chunks_metadata:
            text_words = set(meta.get("text", "").lower().split())
            overlap = len(query_words.intersection(text_words))
            scores.append(float(overlap))
        scores_arr = np.array(scores, dtype=np.float32)
        if scores_arr.max() > 0:
            scores_arr = scores_arr / scores_arr.max()
        return scores_arr

    def retrieve(
        self,
        query: str,
        k: int = 5,
        category_filter: Optional[str] = None,
        source_diversity: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k evidence chunks using precomputed embeddings and NumPy cosine similarity.
        """
        if self.embeddings_matrix is None or len(self.chunks_metadata) == 0:
            return []

        q_vec = self.encode_query(query)

        if isinstance(q_vec, np.ndarray) and q_vec.ndim == 1 and q_vec.shape[0] == self.embeddings_matrix.shape[1]:
            # Exact cosine similarity matrix dot-product
            scores = np.dot(self.embeddings_matrix, q_vec)
        elif isinstance(q_vec, np.ndarray) and q_vec.shape[0] == len(self.chunks_metadata):
            scores = q_vec
        else:
            scores = np.zeros(len(self.chunks_metadata), dtype=np.float32)

        top_indices = np.argsort(scores)[::-1]

        raw_evidence = []
        for idx in top_indices:
            meta = self.chunks_metadata[idx]
            score = float(scores[idx])

            if category_filter and meta.get("category") != category_filter:
                continue

            item = dict(meta)
            item["score"] = round(score, 4)
            raw_evidence.append(item)

        if not source_diversity:
            results = raw_evidence[:k]
            for rank_idx, item in enumerate(results):
                item["rank"] = rank_idx + 1
            return results

        diversified = []
        source_counts = {}

        for item in raw_evidence:
            src = item.get("source_id", item.get("document"))
            count = source_counts.get(src, 0)
            if count < 2 or len(source_counts) < 2:
                diversified.append(item)
                source_counts[src] = count + 1
            if len(diversified) == k:
                break

        if len(diversified) < k:
            for item in raw_evidence:
                if item not in diversified:
                    diversified.append(item)
                if len(diversified) == k:
                    break

        for rank_idx, item in enumerate(diversified):
            item["rank"] = rank_idx + 1

        return diversified
