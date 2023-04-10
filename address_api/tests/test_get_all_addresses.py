from fastapi.testclient import TestClient
from api.main import app
BASE_URL = "/get_all_addresses"


def test_get_all_addresses(client: TestClient = TestClient(app)):
    response = client.get(url=BASE_URL)
    assert response.is_success
    assert response.status_code == 200



