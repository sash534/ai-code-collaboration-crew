from crewai import Agent
from src.config import get_llm
from src.tools.splunk_tool import (
    SplunkSearchErrorsTool,
    SplunkAlertsTool,
    SplunkApiErrorsTool,
)


def get_detector():
    return Agent(
        role="Incident Detector",
        goal=(
            "Detect and characterize production incidents by querying monitoring systems. "
            "Identify the affected service, error patterns, error rates, and time window."
        ),
        backstory=(
            "You are an experienced SRE who is the first responder to production alerts. "
            "You know how to quickly pull the right signals from monitoring dashboards — "
            "active alerts, error spikes, and affected endpoints — to form an initial "
            "incident signal that other team members can act on. You are methodical and "
            "always start by checking active alerts, then drill into error logs and API "
            "error rates."
        ),
        tools=[
            SplunkSearchErrorsTool(),
            SplunkAlertsTool(),
            SplunkApiErrorsTool(),
        ],
        allow_delegation=False,
        llm=get_llm(),
        verbose=True,
    )
