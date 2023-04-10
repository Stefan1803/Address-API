from fastapi.testclient import TestClient
from api.main import app


BASE_URL = "/update_address"


def test_update_address(client: TestClient = TestClient(app)):
    response = client.put(
        url=BASE_URL,
        json={
                "id": 1,
                "new_name": "New store",
                "new_description": "Store for car parts"
        }
    )
    assert response.is_success
    assert response.status_code == 200
    assert response.json() == {"Success": "Address updated!"}


def test_create_address_wrong_id(client: TestClient = TestClient(app)):
    response = client.put(
        url=BASE_URL,
        json={
                "id": 1111,
                "new_name": "New store",
                "new_description": "Store for car parts"
        }
    )

    assert response.status_code == 404

