from crewai import Agent
from src.config import get_llm
from src.tools.splunk_tool import (
    SplunkSearchLogsTool,
    SplunkStackTracesTool,
    SplunkDeploysTool,
)


def get_log_analyst():
    return Agent(
        role="Log Analyst",
        goal=(
            "Perform deep root cause analysis by examining stack traces, log patterns, "
            "and deployment history. Identify the exact cause of the incident and correlate "
            "it with recent changes."
        ),
        backstory=(
            "You are a senior debugging specialist who excels at reading stack traces and "
            "correlating error patterns with system changes. You always look for: "
            "(1) the most common exception and where it originates in code, "
            "(2) recent deployments or config changes that could have triggered the issue, "
            "(3) the exact timeline of when errors started vs when changes were made. "
            "You provide a clear root cause hypothesis backed by evidence from logs."
        ),
        tools=[
            SplunkSearchLogsTool(),
            SplunkStackTracesTool(),
            SplunkDeploysTool(),
        ],
        allow_delegation=False,
        llm=get_llm(),
        verbose=True,
    )
