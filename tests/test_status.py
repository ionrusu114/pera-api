from fastapi.testclient import TestClient
from pera_fastapi.main import app

from pera_fastapi.settings import settings

def test_status():
    """
    Test status
    """
    client = TestClient(app)
    result = client.get("groups")
    assert result.status_code == 200
    # assert result.json() == {"status": "ok"}