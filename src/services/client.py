"""HTTP client abstraction for service integrations.

Each service base URL defaults to the local mock service.
Set environment variables to point to real services later.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SERVICE_URLS = {
    "splunk": os.getenv("SPLUNK_BASE_URL", "http://localhost:8001/api"),
    "jira": os.getenv("JIRA_BASE_URL", "http://localhost:8002/api"),
    "slack": os.getenv("SLACK_BASE_URL", "http://localhost:8003/api"),
    "github": os.getenv("GITHUB_BASE_URL", "http://localhost:8004/api"),
    "gdrive": os.getenv("GDRIVE_BASE_URL", "http://localhost:8005/api"),
}


class ServiceClient:
    def __init__(self, service_name: str, timeout: float = 30.0):
        self.base_url = SERVICE_URLS[service_name]
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def get(self, path: str, **params) -> dict:
        resp = self.client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, **json_data) -> dict:
        resp = self.client.post(path, json=json_data)
        resp.raise_for_status()
        return resp.json()

    def put(self, path: str, **json_data) -> dict:
        resp = self.client.put(path, json=json_data)
        resp.raise_for_status()
        return resp.json()
