from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from src.services.client import ServiceClient


class CreateDocInput(BaseModel):
    title: str = Field(..., description="Document title (e.g. 'Post-Incident Report: Payment Service Outage 2026-03-28')")
    content: str = Field(..., description="Full document content in markdown format. Include: Executive Summary, Timeline, Root Cause, Impact, Remediation, Action Items.")


class UpdateDocInput(BaseModel):
    doc_id: str = Field(..., description="Document ID to update")
    content: str = Field(..., description="Content to append or replace")
    mode: str = Field(default="append", description="'append' to add content, 'replace' to overwrite")


class GDriveCreateDocTool(BaseTool):
    name: str = "create_document"
    description: str = "Create a post-incident report document. Include structured sections: Executive Summary, Timeline, Root Cause Analysis, Impact Assessment, Remediation Steps, and Action Items."
    args_schema: type[BaseModel] = CreateDocInput

    def _run(self, title: str, content: str) -> str:
        client = ServiceClient("gdrive")
        result = client.post("/documents", title=title, content=content)
        return json.dumps(result, indent=2)


class GDriveUpdateDocTool(BaseTool):
    name: str = "update_document"
    description: str = "Update an existing document by appending or replacing content."
    args_schema: type[BaseModel] = UpdateDocInput

    def _run(self, doc_id: str, content: str, mode: str = "append") -> str:
        client = ServiceClient("gdrive")
        resp = client.client.put(f"/documents/{doc_id}", json={"content": content, "mode": mode})
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)
