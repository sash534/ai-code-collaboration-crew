from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from src.services.client import ServiceClient


class ServiceInput(BaseModel):
    service: str = Field(..., description="Service name (e.g. 'payment-svc', 'auth-svc')")


class SearchLogsInput(BaseModel):
    query: str = Field(..., description="Search query string to filter logs (e.g. 'deploy', 'config change', 'ERROR')")
    service: str = Field(..., description="Service name to filter by (e.g. 'payment-svc')")


class ApiErrorsInput(BaseModel):
    endpoint: str = Field(..., description="API endpoint path to filter by (e.g. '/api/v1/payments/process')")


class SplunkSearchErrorsTool(BaseTool):
    name: str = "search_errors"
    description: str = "Search for error-level log entries. Returns error logs with timestamps, hosts, messages, and trace IDs for a given service."
    args_schema: type[BaseModel] = ServiceInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/search/errors", service=service)
        return json.dumps(result, indent=2)


class SplunkSearchLogsTool(BaseTool):
    name: str = "search_logs"
    description: str = "Search logs with a text query for a service. Returns matching log entries across all levels (INFO, WARN, ERROR). Useful for finding deploy events, config changes, and correlating timelines."
    args_schema: type[BaseModel] = SearchLogsInput

    def _run(self, query: str, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/search/logs", query=query, service=service)
        return json.dumps(result, indent=2)


class SplunkStackTracesTool(BaseTool):
    name: str = "get_stack_traces"
    description: str = "Get stack traces and exceptions for a service. Returns exception types, stack frames, occurrence counts, and affected hosts."
    args_schema: type[BaseModel] = ServiceInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/stack_traces", service=service)
        return json.dumps(result, indent=2)


class SplunkApiErrorsTool(BaseTool):
    name: str = "search_api_errors"
    description: str = "Search for API endpoint errors with HTTP status codes, error counts, and time ranges."
    args_schema: type[BaseModel] = ApiErrorsInput

    def _run(self, endpoint: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/search/api_errors", endpoint=endpoint)
        return json.dumps(result, indent=2)


class SplunkHostsTool(BaseTool):
    name: str = "get_hosts"
    description: str = "List all hosts and their health status (healthy, degraded, critical). Useful for determining blast radius."
    args_schema: type[BaseModel] = ServiceInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/hosts")
        return json.dumps(result, indent=2)


class SplunkAlertsTool(BaseTool):
    name: str = "get_alerts"
    description: str = "List all currently active alerts/alarms from the monitoring system. Returns alert names, severity, trigger times."
    args_schema: type[BaseModel] = ServiceInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/alerts")
        return json.dumps(result, indent=2)


class SplunkDeploysTool(BaseTool):
    name: str = "get_recent_deploys"
    description: str = "Get recent deployment events. Returns commit SHAs, authors, timestamps, and changed files. Useful for correlating incidents with recent deployments."
    args_schema: type[BaseModel] = ServiceInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/deploys")
        return json.dumps(result, indent=2)
