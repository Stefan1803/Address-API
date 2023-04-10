from fastapi.testclient import TestClient
from api.main import app

BASE_URL = "/get_address"


def test_get_addresses(latitude: float = 1.5, longitude: float = 1.3, distance: float = 30, client: TestClient = TestClient(app)):
    response = client.get(url=BASE_URL, params={"latitude": latitude, "longitude": longitude, "distance": distance})

    assert response.is_success
    assert response.status_code == 200
