from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from src.services.client import ServiceClient


class CreateTicketInput(BaseModel):
    summary: str = Field(..., description="Ticket title/summary")
    description: str = Field(..., description="Detailed ticket description with incident context")
    priority: str = Field(..., description="Priority: Critical, High, Medium, or Low")


class UpdateTicketInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID (e.g. INC-1)")
    status: str = Field(..., description="New status: Open, In Progress, Resolved, or Closed")


class ReadTicketInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID to read (e.g. INC-1)")


class JiraCreateTicketTool(BaseTool):
    name: str = "create_jira_ticket"
    description: str = "Create an incident ticket in the ticketing system. Include severity, affected service, root cause summary, and impact in the description. Returns the created ticket with its ID."
    args_schema: type[BaseModel] = CreateTicketInput

    def _run(self, summary: str, description: str, priority: str) -> str:
        client = ServiceClient("jira")
        result = client.post(
            "/tickets",
            summary=summary,
            description=description,
            priority=priority,
            project="INC",
            issuetype="Incident",
        )
        return json.dumps(result, indent=2)


class JiraUpdateTicketTool(BaseTool):
    name: str = "update_jira_ticket"
    description: str = "Update the status of an existing incident ticket."
    args_schema: type[BaseModel] = UpdateTicketInput

    def _run(self, ticket_id: str, status: str) -> str:
        client = ServiceClient("jira")
        resp = client.client.put(f"/tickets/{ticket_id}", json={"status": status})
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
