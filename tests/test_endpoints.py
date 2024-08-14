import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_create_user():
    user_data = {
        "uid": "user123",
        "first_name": "John",
        "last_name": "Doe",
        "dob": "01012000",
        "phone_number": "91-1234567890",
        "email": "john.doe@example.com"
    }
    response = client.post("/users/", params=user_data)
    assert response.status_code == 200
    assert response.json()["uid"] == user_data["uid"]

def test_create_user_validation_error():
    user_data = {
        "uid": "user123",
        "first_name": "John",
        "last_name": "Doe",
        "dob": "InvalidDate",  # Invalid date format
        "phone_number": "InvalidPhone",  # Invalid phone number format
        "email": "notanemail"  # Invalid email format
    }
    response = client.post("/users/", params=user_data)
    assert response.status_code == 422


def test_update_user():
    user_data = {
        "uid": "user123",
        "first_name": "Jane",
        "last_name": "Smith",
        "dob": "01011990",
        "phone_number": "91-0987654321",
        "email": "jane.smith@example.com"
    }
    response = client.put("/users/", params=user_data)
    assert response.status_code == 200
    assert response.json()["name"]["first_name"] == user_data["first_name"]

def test_update_user_validation_error():
    user_data = {
        "uid": "user123",
        "first_name": "Jane",
        "last_name": "Smith",
        "dob": "InvalidDate",
        "phone_number": "InvalidPhone",
        "email": "notanemail"
    }
    response = client.put("/users/", params=user_data)
    assert response.status_code == 422


def test_get_all_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_users_with_invalid_auth():
    response = client.get("/users/", params={"auth_uid": "invalid"})
    assert response.status_code == 422

def test_get_user():
    response = client.get("/users/user123")
    assert response.status_code == 200
    assert response.json()["uid"] == "user123"

def test_get_user_not_found():
    response = client.get("/users/invalid_uid")
    assert response.status_code == 404  # Assuming 404 for not found

def test_get_user():
    response = client.get("/users/user123")
    assert response.status_code == 200
    assert response.json()["uid"] == "user123"

def test_get_user_not_found():
    response = client.get("/users/invalid_uid")
    assert response.status_code == 404  # Assuming 404 for not found

def test_delete_user():
    response = client.delete("/users/user123")
    assert response.status_code == 200
    assert response.json() == {}

def test_delete_user_not_found():
    response = client.delete("/users/invalid_uid")
    assert response.status_code == 404  # Assuming 404 for not found

def test_add_job_to_user():
    job_data = {
        "uid": "user123",
        "job_id": 1
    }
    response = client.post("/users/saved_jobs", params=job_data)
    assert response.status_code == 200
    assert response.json() == {}

def test_add_job_to_user_validation_error():
    job_data = {
        "uid": "user123",
        "job_id": "invalid_id"  # Invalid job ID
    }
    response = client.post("/users/saved_jobs", params=job_data)
    assert response.status_code == 422

def test_remove_job_from_user():
    job_data = {
        "uid": "user123",
        "job_id": 1
    }
    response = client.delete("/users/saved_jobs", params=job_data)
    assert response.status_code == 200

def test_remove_job_from_user_validation_error():
    job_data = {
        "uid": "user123",
        "job_id": "invalid_id"  # Invalid job ID
    }
    response = client.delete("/users/saved_jobs", params=job_data)
    assert response.status_code == 422



