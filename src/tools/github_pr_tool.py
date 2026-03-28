"""GitHub PR review tools.

Fetches pull request metadata and file diffs from the GitHub REST API.
Defaults to api.github.com for real PRs; set GITHUB_BASE_URL to route
through the local mock (http://localhost:8004/api) for offline testing.
"""

import json
import os

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

DEFAULT_OWNER = "sash534"
DEFAULT_REPO = "ai-code-collaboration-crew"


def _github_client() -> httpx.Client:
    base_url = os.getenv("GITHUB_BASE_URL", "")
    headers = {"Accept": "application/vnd.github+json"}

    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if base_url:
        return httpx.Client(base_url=base_url, headers=headers, timeout=30.0)
    return httpx.Client(
        base_url="https://api.github.com", headers=headers, timeout=30.0
    )


class FetchPRInput(BaseModel):
    pr_number: int = Field(..., description="Pull request number to fetch")
    owner: str = Field(default=DEFAULT_OWNER, description="Repository owner")
    repo: str = Field(default=DEFAULT_REPO, description="Repository name")


class PRFilesInput(BaseModel):
    pr_number: int = Field(..., description="Pull request number")
    owner: str = Field(default=DEFAULT_OWNER, description="Repository owner")
    repo: str = Field(default=DEFAULT_REPO, description="Repository name")


class GitHubFetchPRTool(BaseTool):
    name: str = "fetch_pull_request"
    description: str = (
        "Fetch pull request metadata including title, description, author, "
        "state, and branch info. Use this first to understand what the PR is about."
    )
    args_schema: type[BaseModel] = FetchPRInput

    def _run(self, pr_number: int, owner: str = DEFAULT_OWNER, repo: str = DEFAULT_REPO) -> str:
        client = _github_client()
        try:
            resp = client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(data, indent=2)
        except httpx.HTTPStatusError as exc:
            return json.dumps({"error": str(exc), "status_code": exc.response.status_code})
        finally:
            client.close()


class GitHubPRFilesTool(BaseTool):
    name: str = "list_pr_files"
    description: str = (
        "List all files changed in a pull request with their patch diffs. "
        "Use this to review the actual code changes line by line."
    )
    args_schema: type[BaseModel] = PRFilesInput

    def _run(self, pr_number: int, owner: str = DEFAULT_OWNER, repo: str = DEFAULT_REPO) -> str:
        client = _github_client()
        try:
            resp = client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(data, indent=2)
        except httpx.HTTPStatusError as exc:
            return json.dumps({"error": str(exc), "status_code": exc.response.status_code})
        finally:
            client.close()
