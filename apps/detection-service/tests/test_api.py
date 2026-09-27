import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

TEST_DIR = Path(__file__).resolve().parent
TEST_IMAGE_PATH = TEST_DIR / "test_road.jpg"


@pytest.fixture(scope="module")
def client():
    """
    Module-scoped TestClient fixture that enters the FastAPI lifespan context manager.
    Ensures app.state.detector and RF-DETR model checkpoint are loaded at test startup.
    """
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def create_dummy_image_bytes() -> bytes:
    """Helper to generate an in-memory JPEG image for testing."""
    img = Image.new("RGB", (640, 480), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health_check_endpoint(client):
    """Test GET /health endpoint returns HTTP 200 and health status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert data["model_name"] == "RFDETRMedium"
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_predict_with_valid_image(client):
    """Test POST /predict with a valid road image."""
    if TEST_IMAGE_PATH.exists():
        image_bytes = TEST_IMAGE_PATH.read_bytes()
    else:
        image_bytes = create_dummy_image_bytes()

    response = client.post(
        "/predict",
        files={"file": ("test_road.jpg", image_bytes, "image/jpeg")},
        params={"threshold": 0.3}
    )

    assert response.status_code == 200
    data = response.json()

    # Validate required JSON schema keys
    assert "detections" in data
    assert isinstance(data["detections"], list)
    assert "damage_type" in data
    assert "confidence" in data
    assert "bounding_box" in data
    assert "detection_count" in data
    assert "image_width" in data
    assert "image_height" in data

    # Verify data types
    assert isinstance(data["detection_count"], int)
    assert isinstance(data["image_width"], int)
    assert isinstance(data["image_height"], int)
    assert data["detection_count"] == len(data["detections"])

    # Ensure raw image array is NOT returned
    assert "source_image" not in data
    assert "image_array" not in data

    # Verify detection structure if detections exist
    if data["detection_count"] > 0:
        det = data["detections"][0]
        assert "damage_type" in det
        assert "confidence" in det
        assert "bounding_box" in det
        assert "class_id" in det
        assert len(det["bounding_box"]) == 4


def test_predict_with_invalid_file_type(client):
    """Test POST /predict rejects non-image text file with HTTP 400."""
    text_content = b"This is a text file, not an image."
    response = client.post(
        "/predict",
        files={"file": ("document.txt", text_content, "text/plain")}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid file type" in data["detail"] or "image" in data["detail"]


def test_predict_with_corrupted_image_bytes(client):
    """Test POST /predict rejects corrupt image bytes with HTTP 400."""
    corrupt_bytes = b"GIF89a corrupted image payload structure"
    response = client.post(
        "/predict",
        files={"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
