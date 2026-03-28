from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import json
from src.services.client import ServiceClient


class SearchErrorsInput(BaseModel):
    service: str = Field(..., description="Service name to search errors for (e.g. 'payment-svc')")
    host: Optional[str] = Field(default=None, description="Specific hostname to filter by")


class SearchLogsInput(BaseModel):
    query: str = Field(..., description="Search query string to filter logs")
    service: Optional[str] = Field(default=None, description="Service name to filter by")


class StackTracesInput(BaseModel):
    service: str = Field(..., description="Service name to get stack traces for")


class ApiErrorsInput(BaseModel):
    endpoint: str = Field(..., description="API endpoint path to filter by (e.g. '/api/v1/payments/process')")


class HostsInput(BaseModel):
    service: str = Field(..., description="Service name to get hosts for (e.g. 'payment-svc')")


class AlertsInput(BaseModel):
    service: str = Field(..., description="Service name to check alerts for (e.g. 'payment-svc')")


class DeploysInput(BaseModel):
    service: str = Field(..., description="Service name to get recent deploys for (e.g. 'payment-svc')")


class SplunkSearchErrorsTool(BaseTool):
    name: str = "search_errors"
    description: str = "Search for error-level log entries from the logging/SIEM system. Returns error logs with timestamps, hosts, messages, and trace IDs."
    args_schema: type[BaseModel] = SearchErrorsInput

    def _run(self, service: str, host: Optional[str] = None) -> str:
        client = ServiceClient("splunk")
        params = {"service": service}
        if host:
            params["host"] = host
        result = client.get("/search/errors", **params)
        return json.dumps(result, indent=2)


class SplunkSearchLogsTool(BaseTool):
    name: str = "search_logs"
    description: str = "Search logs with a text query. Returns matching log entries across all levels (INFO, WARN, ERROR). Useful for finding deploy events, config changes, and correlating timelines."
    args_schema: type[BaseModel] = SearchLogsInput

    def _run(self, query: str, service: Optional[str] = None) -> str:
        client = ServiceClient("splunk")
        params = {"query": query}
        if service:
            params["service"] = service
        result = client.get("/search/logs", **params)
        return json.dumps(result, indent=2)


class SplunkStackTracesTool(BaseTool):
    name: str = "get_stack_traces"
    description: str = "Get stack traces and exceptions from the logging system. Returns exception types, stack frames, occurrence counts, and affected hosts."
    args_schema: type[BaseModel] = StackTracesInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/stack_traces", service=service)
        return json.dumps(result, indent=2)


class SplunkApiErrorsTool(BaseTool):
    name: str = "search_api_errors"
    description: str = "Search for API endpoint errors with HTTP status codes, error counts, and time ranges. Useful for identifying which endpoints are failing."
    args_schema: type[BaseModel] = ApiErrorsInput

    def _run(self, endpoint: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/search/api_errors", endpoint=endpoint)
        return json.dumps(result, indent=2)


class SplunkHostsTool(BaseTool):
    name: str = "get_hosts"
    description: str = "List all hosts and their health status (healthy, degraded, critical). Useful for determining blast radius."
    args_schema: type[BaseModel] = HostsInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/hosts")
        return json.dumps(result, indent=2)


class SplunkAlertsTool(BaseTool):
    name: str = "get_alerts"
    description: str = "List all currently active alerts/alarms from the monitoring system. Returns alert names, severity, trigger times."
    args_schema: type[BaseModel] = AlertsInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/alerts")
        return json.dumps(result, indent=2)


class SplunkDeploysTool(BaseTool):
    name: str = "get_recent_deploys"
    description: str = "Get recent deployment events. Returns commit SHAs, authors, timestamps, and changed files. Useful for correlating incidents with recent deployments."
    args_schema: type[BaseModel] = DeploysInput

    def _run(self, service: str) -> str:
        client = ServiceClient("splunk")
        result = client.get("/deploys")
        return json.dumps(result, indent=2)
