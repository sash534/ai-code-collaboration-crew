from crewai import Agent
from src.config import get_llm
from src.tools.github_pr_tool import GitHubFetchPRTool, GitHubPRFilesTool


def get_pr_reviewer():
    return Agent(
        role="Senior PR Reviewer",
        goal=(
            "Analyze pull request diffs and flag security vulnerabilities, bugs, "
            "performance regressions, style violations, and missing test coverage. "
            "Produce a concise, actionable review summary."
        ),
        backstory=(
            "You are a principal engineer who has reviewed thousands of pull requests. "
            "You focus on what matters:\n"
            "1. Security — credentials in code, SQL injection, unsafe deserialization\n"
            "2. Bugs — off-by-one errors, null dereferences, race conditions\n"
            "3. Performance — O(n^2) loops, missing indexes, unbounded queries\n"
            "4. Style — inconsistent naming, dead code, overly complex logic\n"
            "5. Tests — untested edge cases, missing error-path coverage\n\n"
            "You always fetch the PR metadata first to understand context, then "
            "review every changed file. You classify each finding as Critical, "
            "Warning, or Info and provide a one-line fix suggestion."
        ),
        tools=[
            GitHubFetchPRTool(),
            GitHubPRFilesTool(),
        ],
        allow_delegation=False,
        llm=get_llm(),
        verbose=True,
    )
