from main import app, get_db, url_shortener, short_code_generator
from fastapi.testclient import TestClient
from fastapi import HTTPException
from test_database import TestSessionLocal
import pytest, os


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_shorten():
    response = client.post("/shorten", json={"long_url": "https://www.example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "short_code" in data


def test_url_shortener():
    with pytest.raises(ValueError):
        assert url_shortener("https://www.example.com", salt=True)


def test_short_code_generator():
    assert short_code_generator("www.example.com") == short_code_generator(
        "www.example.com"
    )


def test_get_all_codes():
    response = client.get("/show")
    assert response.status_code == 200
    assert response.json() == {"error": "Invalid query parameter"}

    response = client.get("/show", params={"show": "not"})
    assert response.status_code == 200
    assert response.json() == {"error": "Invalid query parameter"}


def test_get_access_logs():
    key = os.getenv("SECRET_KEY")
    response = client.get("/admin", params={"passwrd": key})
    assert response.status_code == 200
    assert response.json() == {"error": "Please provide code"}

    response = client.get("/admin")
    assert response.status_code == 200
    assert response.json() == {"error": "Unauthorized Access"}


def test_resolve():
    code = 0
    response = client.get(f"/{code}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Short code not found"}
