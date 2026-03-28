from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import json
from src.services.client import ServiceClient


class CreateTicketInput(BaseModel):
    summary: str = Field(..., description="Ticket title/summary")
    description: str = Field(..., description="Detailed ticket description with incident context")
    priority: str = Field(default="Critical", description="Priority: Critical, High, Medium, Low")
    labels: list[str] = Field(default_factory=list, description="Labels to add to the ticket")


class UpdateTicketInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID (e.g. INC-1)")
    status: Optional[str] = Field(default=None, description="New status: Open, In Progress, Resolved, Closed")
    description: Optional[str] = Field(default=None, description="Updated description")
    assignee: Optional[str] = Field(default=None, description="Assignee username")


class ReadTicketInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID to read (e.g. INC-1)")


class JiraCreateTicketTool(BaseTool):
    name: str = "create_jira_ticket"
    description: str = "Create an incident ticket in the ticketing system. Include severity, affected service, root cause summary, and impact in the description."
    args_schema: type[BaseModel] = CreateTicketInput

    def _run(self, summary: str, description: str, priority: str = "Critical", labels: list[str] = []) -> str:
        client = ServiceClient("jira")
        result = client.post(
            "/tickets",
            summary=summary,
            description=description,
            priority=priority,
            labels=labels,
            project="INC",
            issuetype="Incident",
        )
        return json.dumps(result, indent=2)


class JiraUpdateTicketTool(BaseTool):
    name: str = "update_jira_ticket"
    description: str = "Update an existing incident ticket. Can change status, description, or assignee."
    args_schema: type[BaseModel] = UpdateTicketInput

    def _run(self, ticket_id: str, status: Optional[str] = None, description: Optional[str] = None, assignee: Optional[str] = None) -> str:
        client = ServiceClient("jira")
        update_data = {}
        if status:
            update_data["status"] = status
        if description:
            update_data["description"] = description
        if assignee:
            update_data["assignee"] = assignee
        resp = client.client.put(f"/tickets/{ticket_id}", json=update_data)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)


class JiraReadTicketTool(BaseTool):
    name: str = "read_jira_ticket"
    description: str = "Read the details of an existing ticket by its ID."
    args_schema: type[BaseModel] = ReadTicketInput

    def _run(self, ticket_id: str) -> str:
        client = ServiceClient("jira")
        result = client.get(f"/tickets/{ticket_id}")
        return json.dumps(result, indent=2)
