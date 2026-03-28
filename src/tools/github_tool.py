from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from src.services.client import ServiceClient

MOCK_OWNER = "acme"
MOCK_REPO = "platform"


class SearchCodeInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant code (e.g. file name, class name, function name)")


class GetCommitInput(BaseModel):
    sha: str = Field(..., description="Commit SHA to retrieve details for")


class CreatePRInput(BaseModel):
    title: str = Field(..., description="Pull request title")
    body: str = Field(..., description="Pull request description with context about the fix")
    head: str = Field(..., description="Branch name containing the fix")


class GitHubSearchCodeTool(BaseTool):
    name: str = "search_code"
    description: str = "Search the code repository for files, functions, or code patterns. Returns matching file paths, commit SHAs, and code snippets."
    args_schema: type[BaseModel] = SearchCodeInput

    def _run(self, query: str) -> str:
        client = ServiceClient("github")
        result = client.get(f"/repos/{MOCK_OWNER}/{MOCK_REPO}/search", q=query)
        return json.dumps(result, indent=2)


class GitHubListCommitsTool(BaseTool):
    name: str = "list_recent_commits"
    description: str = "List recent commits in the repository. Returns commit SHAs, authors, messages, timestamps, and changed files."

    def _run(self) -> str:
        client = ServiceClient("github")
        result = client.get(f"/repos/{MOCK_OWNER}/{MOCK_REPO}/commits")
        return json.dumps(result, indent=2)


class GitHubGetCommitTool(BaseTool):
    name: str = "get_commit_details"
    description: str = "Get full details of a specific commit including the diff. Use this to inspect the exact code changes in a suspicious commit."
    args_schema: type[BaseModel] = GetCommitInput

    def _run(self, sha: str) -> str:
        client = ServiceClient("github")
        result = client.get(f"/repos/{MOCK_OWNER}/{MOCK_REPO}/commits/{sha}")
        return json.dumps(result, indent=2)


class GitHubCreatePRTool(BaseTool):
    name: str = "create_pull_request"
    description: str = "Create a pull request to fix or revert the problematic code. Include the root cause and fix description in the body."
    args_schema: type[BaseModel] = CreatePRInput

    def _run(self, title: str, body: str, head: str) -> str:
        client = ServiceClient("github")
        result = client.post(
            f"/repos/{MOCK_OWNER}/{MOCK_REPO}/pulls",
            title=title,
            body=body,
            head=head,
            base="main",
        )
        return json.dumps(result, indent=2)
