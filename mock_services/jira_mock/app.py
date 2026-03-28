import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Jira Mock Service", version="1.0.0")

tickets: dict[str, dict] = {}
ticket_counter = 0


class CreateTicketRequest(BaseModel):
    project: str = "INC"
    summary: str
    description: str
    issuetype: str = "Incident"
    priority: str = "Critical"
    labels: list[str] = []


class UpdateTicketRequest(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[list[str]] = None
    assignee: Optional[str] = None


@app.post("/api/tickets")
async def create_ticket(req: CreateTicketRequest):
    global ticket_counter
    ticket_counter += 1
    ticket_id = f"{req.project}-{ticket_counter}"
    ticket = {
        "id": ticket_id,
        "key": ticket_id,
        "project": req.project,
        "summary": req.summary,
        "description": req.description,
        "issuetype": req.issuetype,
        "priority": req.priority,
        "status": "Open",
        "labels": req.labels,
        "assignee": None,
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "comments": [],
    }
    tickets[ticket_id] = ticket
    return ticket


@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return tickets[ticket_id]


@app.put("/api/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, req: UpdateTicketRequest):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    ticket = tickets[ticket_id]
    for field, value in req.model_dump(exclude_none=True).items():
        ticket[field] = value
    ticket["updated"] = datetime.now(timezone.utc).isoformat()
    return ticket


@app.get("/api/tickets")
async def list_tickets():
    return {"results": list(tickets.values()), "total": len(tickets)}


@app.get("/api/search")
async def search_tickets(jql: str = ""):
    results = list(tickets.values())
    if jql:
        jql_lower = jql.lower()
        if "status" in jql_lower:
            for status_val in ("open", "in progress", "resolved", "closed"):
                if status_val in jql_lower:
                    results = [t for t in results if t["status"].lower() == status_val]
        if "project" in jql_lower:
            for t in list(results):
                if t["project"].lower() not in jql_lower:
                    results.remove(t)
    return {"results": results, "total": len(results)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "tickets_count": len(tickets)}
