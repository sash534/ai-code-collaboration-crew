import json
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="GitHub Mock Service", version="1.0.0")

scenario_data: dict = {}
pull_requests: list[dict] = []
pr_counter = 0


@app.post("/api/scenario/load")
async def load_scenario(name: str = Query(...)):
    global scenario_data
    path = Path(__file__).parent.parent / "scenarios" / f"{name}.json"
    if not path.exists():
        return {"error": f"Scenario '{name}' not found"}
    scenario_data = json.loads(path.read_text())
    return {"status": "loaded", "scenario": name}


@app.get("/api/repos/{owner}/{repo}/search")
async def search_code(owner: str, repo: str, q: str = ""):
    commits = scenario_data.get("commits", [])
    results = []
    q_lower = q.lower()
    for commit in commits:
        for f in commit.get("files", []):
            if q_lower in f.get("path", "").lower() or q_lower in f.get("diff", "").lower():
                results.append({
                    "path": f["path"],
                    "commit_sha": commit["sha"],
                    "author": commit["author"],
                    "message": commit["message"],
                    "snippet": f.get("diff", "")[:300],
                })
    return {"results": results, "total": len(results)}


@app.get("/api/repos/{owner}/{repo}/commits")
async def list_commits(owner: str, repo: str, count: int = 10):
    commits = scenario_data.get("commits", [])
    simplified = []
    for c in commits[:count]:
        simplified.append({
            "sha": c["sha"],
            "author": c["author"],
            "message": c["message"],
            "timestamp": c["timestamp"],
            "files_changed": [f["path"] for f in c.get("files", [])],
        })
    return {"results": simplified, "total": len(commits)}


@app.get("/api/repos/{owner}/{repo}/commits/{sha}")
async def get_commit(owner: str, repo: str, sha: str):
    commits = scenario_data.get("commits", [])
    for c in commits:
        if c["sha"] == sha or c["sha"].startswith(sha):
            return c
    raise HTTPException(status_code=404, detail=f"Commit {sha} not found")


class CreatePRRequest(BaseModel):
    title: str
    body: str
    head: str
    base: str = "main"


@app.post("/api/repos/{owner}/{repo}/pulls")
async def create_pull_request(owner: str, repo: str, req: CreatePRRequest):
    global pr_counter
    pr_counter += 1
    pr = {
        "id": pr_counter,
        "number": pr_counter,
        "title": req.title,
        "body": req.body,
        "head": req.head,
        "base": req.base,
        "state": "open",
        "html_url": f"https://github.com/{owner}/{repo}/pull/{pr_counter}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user": {"login": "incident-bot"},
    }
    pull_requests.append(pr)
    return pr


@app.get("/api/repos/{owner}/{repo}/pulls/{pr_number}")
async def get_pull_request(owner: str, repo: str, pr_number: int):
    pr_fixture = scenario_data.get("pull_request")
    if pr_fixture and pr_fixture.get("number") == pr_number:
        return pr_fixture

    for pr in pull_requests:
        if pr["number"] == pr_number:
            return pr
    raise HTTPException(status_code=404, detail=f"PR #{pr_number} not found")


@app.get("/api/repos/{owner}/{repo}/pulls/{pr_number}/files")
async def get_pull_request_files(owner: str, repo: str, pr_number: int):
    pr_files = scenario_data.get("pull_request_files", [])
    pr_fixture = scenario_data.get("pull_request")
    if pr_files and pr_fixture and pr_fixture.get("number") == pr_number:
        return pr_files

    raise HTTPException(status_code=404, detail=f"Files for PR #{pr_number} not found")


@app.get("/api/repos/{owner}/{repo}/pulls")
async def list_pull_requests(owner: str, repo: str):
    return {"results": pull_requests, "total": len(pull_requests)}


@app.get("/api/health")
async def health():
    loaded = bool(scenario_data)
    return {"status": "ok", "scenario_loaded": loaded, "prs_count": len(pull_requests)}
