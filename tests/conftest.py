import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault("OPENAI_API_KEY", "test-api-key-for-testing")
os.environ.setdefault("USE_MOCK_DATA", "true")


@pytest.fixture(scope="session")
def client():
    from src.main import app
    with TestClient(app) as c:
        yield c
