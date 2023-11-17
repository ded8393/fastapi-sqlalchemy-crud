from fastapi.testclient import TestClient


def test_root(client: TestClient):
    result = client.get("/")
    assert result.status_code == 200
    assert result.json() == {"message": "Hello World"}
