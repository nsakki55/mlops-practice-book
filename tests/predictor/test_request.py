from fastapi import FastAPI
from fastapi.testclient import TestClient

from mlops.predictor import AdRequest

app = FastAPI()


@app.post("/ad_request")
async def create_ad_request(request: AdRequest):
    return request


client = TestClient(app)


def test_ad_request():
    valid_data = {
        "impression_id": "imp_123456789",
        "logged_at": "2023-05-01T12:34:56Z",
        "user_id": 12345,
        "app_code": 101,
        "os_version": "iOS 15.4",
        "is_4g": 1,
    }

    response = client.post("/ad_request", json=valid_data)
    assert response.status_code == 200
    assert response.json() == valid_data

    missing_field_data = valid_data.copy()
    del missing_field_data["logged_at"]
    response = client.post("/ad_request", json=missing_field_data)
    assert response.status_code == 422

    invalid_type_data = valid_data.copy()
    invalid_type_data["user_id"] = "incorrect_type_user_id"
    response = client.post("/ad_request", json=invalid_type_data)
    assert response.status_code == 422

    unknown_field_data = valid_data.copy()
    unknown_field_data["unknown_field"] = "unknown_value"
    response = client.post("/ad_request", json=unknown_field_data)
    assert response.status_code == 200
    assert "unknown_field" not in response.json()
