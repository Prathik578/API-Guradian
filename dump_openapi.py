import json
from fastapi.testclient import TestClient
from api_guardian.api.app import app

client = TestClient(app)
response = client.get("/openapi.json")
with open("openapi.json", "w") as f:
    f.write(json.dumps(response.json(), indent=2))
