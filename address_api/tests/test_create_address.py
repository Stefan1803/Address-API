from fastapi.testclient import TestClient
from api.main import app


BASE_URL = "/create_address"


def test_create_address(client: TestClient = TestClient(app)):
    response = client.post(
        url=BASE_URL,
        json={

                "latitude": 1.5,
                "longitude": 1.35,
                "name": "Barber shop",
                "description": "Barber shop for men"
        }
    )
    assert response.is_success
    assert response.status_code == 200
    assert response.json() == {"Success": "Address created!"}


def test_create_address_wrong_latitude(client: TestClient = TestClient(app)):
    response = client.post(
        url=BASE_URL,
        json={
                "latitude": 91,
                "longitude": 1.3145,
                "name": "Hotel Grand",
                "description": "5 stars hotel"
        }
    )

    assert response.status_code == 422


def test_create_address_wrong_longitude(client: TestClient = TestClient(app)):
    response = client.post(
        url=BASE_URL,
        json={
                "latitude": 70,
                "longitude": -181,
                "name": "Hotel Grand 2",
                "description": "5 stars hotel"
        }
    )

    assert response.status_code == 422

