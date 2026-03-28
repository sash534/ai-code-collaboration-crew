from crewai import Crew

from src.agents.pr_reviewer import get_pr_reviewer
from src.tasks.pr_review_task import create_pr_review_task


def build_pr_review_crew(
    pr_number: int,
    owner: str = "sash534",
    repo: str = "ai-code-collaboration-crew",
):
    reviewer = get_pr_reviewer()
    review_task = create_pr_review_task(reviewer, pr_number, owner, repo)

    return Crew(
        agents=[reviewer],
        tasks=[review_task],
        verbose=True,
        memory=False,
    )
