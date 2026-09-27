import io
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageOps
import torch
import numpy as np

from rfdetr import RFDETRMedium
from app.schemas import DetectionItem, DetectionResponse

logger = logging.getLogger("detection_service.detector")

# Class mapping according to RDD2022 dataset / checkpoint schema
# 0 = longitudinal_crack, 1 = transverse_crack, 2 = alligator_crack, 4 = pothole (3 also mapped to pothole for safety)
CLASS_MAP: Dict[int, str] = {
    0: "longitudinal_crack",
    1: "transverse_crack",
    2: "alligator_crack",
    3: "pothole",
    4: "pothole"
}

class RoadDamageDetector:
    """
    Inference wrapper for RF-DETR Medium Road Damage Detection model.
    Loads models/checkpoint_best_total.pth once at application startup.
    """

    def __init__(self, checkpoint_path: str = "models/checkpoint_best_total.pth", device: Optional[str] = None):
        self.checkpoint_path = Path(checkpoint_path).resolve()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.is_loaded = False
        self.load_model()

    def load_model(self) -> None:
        """Loads the trained RF-DETR Medium model checkpoint into memory."""
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at path: {self.checkpoint_path}")

        logger.info(f"Loading RF-DETR Medium checkpoint from: {self.checkpoint_path} on device: {self.device}")
        try:
            # Load RF-DETR Medium from verified checkpoint
            
            self.model = RFDETRMedium(
                num_classes=4,
                pretrain_weights=str(self.checkpoint_path),
                trust_checkpoint=True
            )
            self.model.inference(
                compile=False,
                inplace=True,
                dtype=torch.float32
            )
            logger.info("RF-DETR Medium inference optimization completed.")
            self.is_loaded = True
            logger.info("RF-DETR Medium model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load RF-DETR model checkpoint: {e}", exc_info=True)
            self.is_loaded = False
            raise RuntimeError(f"Could not initialize RF-DETR detector: {e}") from e

    def validate_image_bytes(self, image_bytes: bytes) -> Tuple[Image.Image, int, int]:
        """
        Validates raw uploaded bytes, verifies image structure, and converts to RGB PIL Image.
        Returns tuple of (PIL Image, image_width, image_height).
        Raises ValueError for invalid image format or corrupt files.
        """
        if not image_bytes or len(image_bytes) < 10:
            raise ValueError("Uploaded file payload is empty or invalid.")

        try:
            stream = io.BytesIO(image_bytes)
            image = Image.open(stream)
            image.verify() # Verify file integrity

            # Re-open after verify() as verify alters image stream pointer
            stream.seek(0)
            image = Image.open(stream)
            image = ImageOps.exif_transpose(image) # Correct orientation if EXIF present
            image = image.convert("RGB")
            return image, image.width, image.height
        except Exception as e:
            logger.warning(f"Image validation failed: {e}")
            raise ValueError(f"Uploaded file is not a valid or supported image: {e}") from e

    def predict(self, image_bytes: bytes, threshold: float = 0.3) -> DetectionResponse:
        """
        Executes RF-DETR inference on image bytes with confidence threshold.
        Returns structured DetectionResponse payload.
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Detector model is not initialized or loaded.")

        # 1. Validate image & extract dimensions
        image, width, height = self.validate_image_bytes(image_bytes)

        # 2. Perform RF-DETR prediction (disable raw source array in result metadata)
        prediction = self.model.predict(
            image,
            threshold=threshold,
            include_source_image=False
        )

        detection_items: List[DetectionItem] = []

        # 3. Parse Supervision Detections output
        if prediction is not None and hasattr(prediction, "xyxy") and len(prediction.xyxy) > 0:
            boxes = prediction.xyxy # shape: (N, 4) [x_min, y_min, x_max, y_max]
            confidences = getattr(prediction, "confidence", np.ones(len(boxes)))
            class_ids = getattr(prediction, "class_id", np.zeros(len(boxes), dtype=int))

            for box, conf, cid in zip(boxes, confidences, class_ids):
                conf_val = round(float(conf), 4)
                if conf_val < threshold:
                    continue

                cid_int = int(cid)
                damage_type_str = CLASS_MAP.get(cid_int, f"class_{cid_int}")

                bbox_list = [round(float(c), 2) for c in box]

                detection_items.append(
                    DetectionItem(
                        damage_type=damage_type_str,
                        confidence=conf_val,
                        bounding_box=bbox_list,
                        class_id=cid_int
                    )
                )

        # 4. Sort detections descending by confidence score
        detection_items.sort(key=lambda item: item.confidence, reverse=True)

        # 5. Extract primary detection (highest confidence item) if detections exist
        primary_damage_type: Optional[str] = None
        primary_confidence: Optional[float] = None
        primary_bounding_box: Optional[List[float]] = None

        if detection_items:
            primary_item = detection_items[0]
            primary_damage_type = primary_item.damage_type
            primary_confidence = primary_item.confidence
            primary_bounding_box = primary_item.bounding_box

        return DetectionResponse(
            detections=detection_items,
            damage_type=primary_damage_type,
            confidence=primary_confidence,
            bounding_box=primary_bounding_box,
            detection_count=len(detection_items),
            image_width=width,
            image_height=height
        )
