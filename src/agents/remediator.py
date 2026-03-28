from crewai import Agent
from src.config import get_llm
from src.tools.github_tool import (
    GitHubSearchCodeTool,
    GitHubListCommitsTool,
    GitHubGetCommitTool,
    GitHubCreatePRTool,
)


def get_remediator():
    return Agent(
        role="Remediation Engineer",
        goal=(
            "Identify the problematic code change and create a fix or revert pull request. "
            "Search the codebase for the affected files, inspect the suspicious commit, "
            "and open a PR to resolve the issue."
        ),
        backstory=(
            "You are a rapid-response engineer who specializes in hotfixes during incidents. "
            "Your approach: (1) search the code repository for the file/function mentioned "
            "in the root cause analysis, (2) list recent commits to find the one that "
            "introduced the bug, (3) inspect the commit diff to confirm it's the culprit, "
            "(4) create a pull request to revert or fix the issue. You always include "
            "the incident context, root cause, and test plan in your PR description."
        ),
        tools=[
            GitHubSearchCodeTool(),
            GitHubListCommitsTool(),
            GitHubGetCommitTool(),
            GitHubCreatePRTool(),
        ],
        allow_delegation=False,
        llm=get_llm(),
        verbose=True,
    )
