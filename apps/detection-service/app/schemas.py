from typing import List, Optional
from pydantic import BaseModel, Field


class DetectionItem(BaseModel):
    """Schema for an individual detected distress object."""
    damage_type: str = Field(..., description="Class name of detected distress (e.g. pothole, longitudinal_crack)")
    confidence: float = Field(..., description="Detection confidence score between 0.0 and 1.0")
    bounding_box: List[float] = Field(..., description="Bounding box in pixel coordinates [x_min, y_min, x_max, y_max]")
    class_id: int = Field(..., description="Model class index (0=longitudinal_crack, 1=transverse_crack, 2=alligator_crack, 4=pothole)")


class DetectionResponse(BaseModel):
    """Schema for POST /predict API response."""
    detections: List[DetectionItem] = Field(default_factory=list, description="List of all detected distress objects")
    damage_type: Optional[str] = Field(None, description="Primary damage type (highest confidence detection) or None")
    confidence: Optional[float] = Field(None, description="Primary confidence score or None")
    bounding_box: Optional[List[float]] = Field(None, description="Primary bounding box [x_min, y_min, x_max, y_max] or None")
    detection_count: int = Field(..., description="Total number of detected objects exceeding threshold")
    image_width: int = Field(..., description="Width of uploaded image in pixels")
    image_height: int = Field(..., description="Height of uploaded image in pixels")


class HealthResponse(BaseModel):
    """Schema for GET /health API response."""
    status: str = Field(..., description="Health status of the service (e.g. healthy)")
    model_loaded: bool = Field(..., description="Whether the RF-DETR model is loaded and ready")
    model_name: str = Field("RFDETRMedium", description="Name of the detection model architecture")
