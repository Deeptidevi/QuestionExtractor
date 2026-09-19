from fastapi.testclient import TestClient


def test_user_registration_success(client: TestClient):
    payload = {
        "email": "newuser@example.com",
        "password": "Password123!",
        "full_name": "New Student",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_user_registration_duplicate_email(client: TestClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_CONFLICT"


def test_user_login_success(client: TestClient, test_user):
    login_data = {
        "username": test_user.email,
        "password": "SecretPassword123!",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_login_invalid_password(client: TestClient, test_user):
    login_data = {
        "username": test_user.email,
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_get_current_user_profile(client: TestClient, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
