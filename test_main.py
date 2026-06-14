from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

VALID_KEY = "ecosense_dev_key_2026_cdmx_aire"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_sentiment_without_api_key_fails():
    response = client.post(
        "/analyze/sentiment",
        json={"text": "test"}
    )
    assert response.status_code == 401


def test_sentiment_with_wrong_api_key_fails():
    response = client.post(
        "/analyze/sentiment",
        headers={"X-API-Key": "clave_incorrecta"},
        json={"text": "test"}
    )
    assert response.status_code == 403


@patch("main.client.analyze_sentiment")
def test_sentiment_with_valid_key_succeeds(mock_analyze):
    # Simulamos la respuesta de Azure sin gastar créditos reales
    mock_result = type("MockResult", (), {
        "sentiment": "positive",
        "confidence_scores": type("Scores", (), {
            "positive": 0.95,
            "neutral": 0.04,
            "negative": 0.01
        })()
    })()
    mock_analyze.return_value = [mock_result]

    response = client.post(
        "/analyze/sentiment",
        headers={"X-API-Key": VALID_KEY},
        json={"text": "I love this app"}
    )

    assert response.status_code == 200
    assert response.json()["sentiment"] == "positive"
