import json
from pathlib import Path
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="Splunk Mock Service", version="1.0.0")

scenario_data: dict = {}


@app.post("/api/scenario/load")
async def load_scenario(name: str = Query(...)):
    global scenario_data
    path = Path(__file__).parent.parent / "scenarios" / f"{name}.json"
    if not path.exists():
        return {"error": f"Scenario '{name}' not found"}
    scenario_data = json.loads(path.read_text())
    return {"status": "loaded", "scenario": name, "title": scenario_data.get("title")}


@app.get("/api/search/errors")
async def search_errors(
    service: Optional[str] = None,
    host: Optional[str] = None,
    earliest: str = "-1h",
    latest: str = "now",
    count: int = 100,
):
    logs = scenario_data.get("error_logs", [])
    if service:
        logs = [l for l in logs if l.get("service") == service]
    if host:
        logs = [l for l in logs if l.get("host") == host]
    errors = [l for l in logs if l.get("level") in ("ERROR", "FATAL")]
    return {"results": errors[:count], "total": len(errors)}


@app.get("/api/search/logs")
async def search_logs(
    query: str = "",
    service: Optional[str] = None,
    earliest: str = "-1h",
    latest: str = "now",
    count: int = 100,
):
    logs = scenario_data.get("error_logs", [])
    if service:
        logs = [l for l in logs if l.get("service") == service]
    if query:
        q_lower = query.lower()
        logs = [l for l in logs if q_lower in json.dumps(l).lower()]
    return {"results": logs[:count], "total": len(logs)}


@app.get("/api/stack_traces")
async def get_stack_traces(
    service: Optional[str] = None,
    earliest: str = "-1h",
    latest: str = "now",
    count: int = 50,
):
    traces = scenario_data.get("stack_traces", [])
    if service:
        traces = [t for t in traces if t.get("service") == service]
    return {"results": traces[:count], "total": len(traces)}


@app.get("/api/search/api_errors")
async def search_api_errors(
    endpoint: Optional[str] = None,
    earliest: str = "-1h",
    latest: str = "now",
    count: int = 50,
):
    api_errors = scenario_data.get("api_errors", [])
    if endpoint:
        api_errors = [e for e in api_errors if endpoint in e.get("endpoint", "")]
    return {"results": api_errors[:count], "total": len(api_errors)}


@app.get("/api/hosts")
async def get_hosts(index: Optional[str] = None):
    return {"results": scenario_data.get("hosts", []), "total": len(scenario_data.get("hosts", []))}


@app.get("/api/alerts")
async def list_alerts():
    return {"results": scenario_data.get("alerts", []), "total": len(scenario_data.get("alerts", []))}


@app.get("/api/deploys")
async def get_deploys(service: Optional[str] = None):
    deploys = scenario_data.get("deploys", [])
    return {"results": deploys, "total": len(deploys)}


@app.get("/api/health")
async def health():
    loaded = bool(scenario_data)
    return {"status": "ok", "scenario_loaded": loaded, "scenario": scenario_data.get("name")}
