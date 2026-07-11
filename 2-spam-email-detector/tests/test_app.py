import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_prediction_endpoint():
    client = app.test_client()
    response = client.post("/predict", data={"message": "Win a free gift card now!"})
    assert response.status_code == 200
    payload = response.get_json()
    assert "prediction" in payload
    assert "confidence" in payload
