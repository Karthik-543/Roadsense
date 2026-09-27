import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from generation.rag_modes import RAGPipeline

app = FastAPI(
    title="RoadSense AI Evidence-Aware RAG API",
    version="1.0.0",
    description="Evidence-Aware Adaptive RAG API for Road Damage Assessment & Maintenance Planning"
)

pipeline = RAGPipeline()

class RoadAssessmentRequest(BaseModel):
    query: Optional[str] = "What maintenance treatment and operational planning is required for the observed distress?"
    image_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    weather: Optional[Dict[str, Any]] = None
    traffic: Optional[Dict[str, Any]] = None
    road_context: Optional[Dict[str, Any]] = None
    detector_results: Optional[Dict[str, Any]] = None
    rag_mode: Optional[str] = "EVIDENCE_AWARE_ADAPTIVE_RAG"

class RoadAssessmentResponse(BaseModel):
    assessment_id: str
    query: str
    rag_mode: str
    latency_ms: float
    damage: List[Dict[str, Any]]
    location_context: Dict[str, Any]
    weather_context: Dict[str, Any]
    traffic_context: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    verification: Dict[str, Any]
    report: str
    uncertainties: List[str]
    sources: List[Dict[str, Any]]

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RoadSense AI RAG Subsystem",
        "version": "1.0.0"
    }

@app.get("/api/v1/config")
def get_config():
    is_openai_active = bool(pipeline.llm.api_key)
    from retrieval.evidence_retriever import RAG_DEPLOYMENT_MODE, HAS_CHROMADB
    store_desc = "Lightweight NumPy Matrix (< 5MB RAM)" if RAG_DEPLOYMENT_MODE == "lightweight" or not HAS_CHROMADB else "ChromaDB (roadsense_knowledge)"
    return {
        "vector_store": store_desc,
        "embedding_model": "all-MiniLM-L6-v2",
        "deployment_mode": RAG_DEPLOYMENT_MODE,
        "llm_enabled": is_openai_active,
        "llm_provider": pipeline.llm.active_provider,
        "model": pipeline.llm.model_name,
        "available_modes": ["NO_RAG", "STANDARD_RAG", "EVIDENCE_AWARE_RAG", "EVIDENCE_AWARE_ADAPTIVE_RAG"]
    }

@app.post("/api/v1/road-assessment", response_model=RoadAssessmentResponse)
def create_road_assessment(req: RoadAssessmentRequest):
    try:
        assessment_id = f"RS-EVAL-{uuid.uuid4().hex[:8].upper()}"

        location_input = {}
        if req.latitude is not None and req.longitude is not None:
            location_input = {
                "latitude": req.latitude,
                "longitude": req.longitude,
                "mapped_road": req.road_context.get("mapped_road", "Mapped Corridor") if req.road_context else "Mapped Road",
                "road_type": req.road_context.get("road_type", "National Highway") if req.road_context else "Road Corridor"
            }

        result = pipeline.run_assessment(
            query=req.query,
            detector_results=req.detector_results,
            location=location_input if location_input else None,
            weather=req.weather,
            traffic=req.traffic,
            mode=req.rag_mode
        )

        return RoadAssessmentResponse(
            assessment_id=assessment_id,
            query=result["query"],
            rag_mode=result["rag_mode"],
            latency_ms=result["latency_ms"],
            damage=result["case_context"]["observations"],
            location_context=result["case_context"]["location_context"],
            weather_context=result["case_context"]["weather_context"],
            traffic_context=result["case_context"]["traffic_context"],
            evidence=result["evidence"],
            verification=result["verification"],
            report=result["report"],
            uncertainties=result["case_context"]["uncertainties"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
