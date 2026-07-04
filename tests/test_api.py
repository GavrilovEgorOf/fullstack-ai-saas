from fastapi.testclient import TestClient

from backend.main import app


def auth_headers(client: TestClient) -> dict[str, str]:
    r = client.post(
        "/api/auth/login",
        json={"email": "demo@team.com", "password": "demo1234"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_and_dashboard():
    with TestClient(app) as client:
        headers = auth_headers(client)
        dash = client.get("/api/dashboard", headers=headers)
        assert dash.status_code == 200
        assert dash.json()["workspace"] == "acme-corp"


def test_ask_and_history():
    with TestClient(app) as client:
        headers = auth_headers(client)
        before = client.get("/api/dashboard", headers=headers).json()["queries_used"]
        ask = client.post("/api/ask", headers=headers, json={"question": "What are API limits?"})
        assert ask.status_code == 200
        assert "answer" in ask.json()
        after = client.get("/api/dashboard", headers=headers).json()["queries_used"]
        assert after == before + 1
        hist = client.get("/api/history", headers=headers)
        assert len(hist.json()) >= 1


def test_knowledge_job_and_export():
    with TestClient(app) as client:
        headers = auth_headers(client)
        created = client.post(
            "/api/knowledge",
            headers=headers,
            json={"title": "Runbook", "content": "Restart service with systemctl restart app"},
        )
        assert created.status_code == 200
        job_id = created.json()["job_id"]
        job = client.get(f"/api/jobs/{job_id}", headers=headers)
        assert job.json()["status"] in {"queued", "running", "done"}
        export = client.get("/api/history/export?format=csv", headers=headers)
        assert export.status_code == 200
        assert "question" in export.text
