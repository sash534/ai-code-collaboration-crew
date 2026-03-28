from crewai import Agent
from src.config import get_llm
from src.tools.splunk_tool import SplunkHostsTool, SplunkSearchLogsTool


def get_triage_agent():
    return Agent(
        role="Incident Triage Specialist",
        goal=(
            "Classify incident severity (SEV-1 through SEV-4) and assess blast radius. "
            "Determine how many users are affected, which hosts are degraded, and what "
            "the business impact is."
        ),
        backstory=(
            "You are an incident commander who makes rapid severity assessments. "
            "Your severity framework:\n"
            "- SEV-1: Revenue-impacting or all-users-affected, requires immediate page\n"
            "- SEV-2: Data integrity or significant feature degradation, affects subset of users\n"
            "- SEV-3: Non-critical service degradation, workaround available\n"
            "- SEV-4: Minor issue, no user impact\n\n"
            "You always check host health to understand blast radius and use error rates "
            "to quantify user impact. You produce a clear severity classification with "
            "justification."
        ),
        tools=[
            SplunkHostsTool(),
            SplunkSearchLogsTool(),
        ],
        allow_delegation=False,
        llm=get_llm(),
        verbose=True,
    )
