import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import DetectionResponse, HealthResponse
from app.detector import RoadDamageDetector

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("detection_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Loads model checkpoint once at startup to keep memory single-loaded.
    """
    logger.info("Initializing RoadSense AI Detection Service...")
    try:
        detector = RoadDamageDetector(checkpoint_path="models/checkpoint_best_total.pth")
        app.state.detector = detector
        logger.info("RF-DETR Medium model loaded and ready for inference.")
    except Exception as e:
        logger.critical(f"Failed to load detection model during startup: {e}", exc_info=True)
        app.state.detector = None

    yield

    logger.info("Shutting down Detection Service...")
    if hasattr(app.state, "detector") and app.state.detector is not None:
        del app.state.detector


app = FastAPI(
    title="RoadSense AI — RF-DETR Detection Service",
    description="Production-ready FastAPI detection microservice for road damage detection using RF-DETR Medium model.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend/backend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health status check endpoint."""
    detector: Optional[RoadDamageDetector] = getattr(app.state, "detector", None)
    is_loaded = detector is not None and detector.is_loaded

    return HealthResponse(
        status="healthy" if is_loaded else "unhealthy",
        model_loaded=is_loaded,
        model_name="RFDETRMedium"
    )


@app.post(
    "/predict",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Inference"],
    summary="Run road damage detection on an uploaded image"
)
async def predict_road_damage(
    file: UploadFile = File(..., description="Uploaded road imagery file (JPEG, PNG, WEBP)"),
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Confidence score threshold for detections")
):
    """
    Accepts an uploaded image file via multipart/form-data.
    Runs RF-DETR Medium object detection model and returns detected road distresses.
    """
    detector: Optional[RoadDamageDetector] = getattr(app.state, "detector", None)
    if detector is None or not detector.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Detection model service is not initialized or unavailable."
        )

    # Validate content type header if present
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Uploaded file must be an image (JPEG, PNG, WEBP)."
        )

    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # Execute detection inference
        result = detector.predict(contents, threshold=threshold)
        return result

    except ValueError as ve:
        logger.warning(f"Bad image payload rejected: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        ) from ve
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Inference error during request processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal model inference error: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
