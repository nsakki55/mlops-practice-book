import pytest
import requests


@pytest.mark.e2e
def test_healthcheck():
    response = requests.get("http://localhost:8080/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"health": "ok"}


@pytest.mark.e2e
def test_prediction_endpoint():
    request_data = {
        "impression_id": "a9e7126a585a69a32bc7414e9d0c0ada",
        "logged_at": "2018-12-13 07:44:00",
        "user_id": 87862,
        "app_code": 127,
        "os_version": "latest",
        "is_4g": 1,
    }

    response = requests.post("http://localhost:8080/predict", headers={"Content-Type": "application/json"}, json=request_data)

    assert response.status_code == 200
    response_data = response.json()
    assert "model" in response_data
    assert "prediction" in response_data
    assert 0 <= response_data["prediction"] <= 1


@pytest.mark.e2e
def test_invalid_request():
    invalid_request = {
        "logged_at": "2018-12-13 07:44:00",
        "user_id": 87862,
        "app_code": 127,
    }

    response = requests.post(
        "http://localhost:8080/predict", headers={"Content-Type": "application/json"}, json=invalid_request
    )

    assert response.status_code == 422
