from uuid import uuid4


def test_register_login_create_and_run_pipeline(client):
    email = f"test-{uuid4()}@example.com"
    password = "password123"

    resp = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 200

    token_resp = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password, "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_payload = {
        "topic": "Large Language Models",
        "keywords": ["LLM", "AI"],
        "search": {"fields": ["title"], "sortBy": "submittedDate", "sortOrder": "descending", "start": 0, "max_results": 2},
        "runtime": {"max_papers": 2, "top_k": 2, "download_concurrency": 1, "retry": 1},
        "providers": {"llm": {"name": "mock"}, "embedding": {"name": "mock"}},
    }
    project_resp = client.post("/api/v1/projects", json=project_payload, headers=headers)
    assert project_resp.status_code == 200
    project = project_resp.json()

    run_resp = client.post(f"/api/v1/projects/{project['id']}/run", headers=headers)
    assert run_resp.status_code == 200

    status_resp = client.get(f"/api/v1/projects/{project['id']}", headers=headers)
    assert status_resp.status_code == 200
    detail = status_resp.json()
    assert detail["status"] == "completed"
    assert detail["progress"] == 100

    papers_resp = client.get(f"/api/v1/projects/{project['id']}/papers", headers=headers)
    assert papers_resp.status_code == 200
    papers = papers_resp.json()
    assert len(papers) > 0

    exports_resp = client.get(f"/api/v1/projects/{project['id']}/exports", headers=headers)
    assert exports_resp.status_code == 200
    exports = exports_resp.json()
    assert any(e["format"] == "md" for e in exports)
