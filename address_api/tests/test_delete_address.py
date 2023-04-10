from fastapi.testclient import TestClient
from api.main import app


BASE_URL = "/delete_address"


def test_create_address_wrong_id(client: TestClient = TestClient(app), id: int = 11111):
    response = client.delete(url=BASE_URL + "/id", params={"id": id})
    assert response.status_code == 422
