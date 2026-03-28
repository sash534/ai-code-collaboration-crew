from crewai import Task


def create_pr_review_task(agent, pr_number: int, owner: str = "sash534", repo: str = "ai-code-collaboration-crew"):
    return Task(
        description=f"""
        Review pull request #{pr_number} in {owner}/{repo}.

        Steps:
        1. Use fetch_pull_request to get PR #{pr_number} metadata (title, author, description, branch).
        2. Use list_pr_files to get every changed file with its patch diff.
        3. For each changed file, evaluate:
           - Security: hardcoded secrets, injection risks, unsafe operations
           - Bugs: logic errors, unhandled exceptions, edge cases
           - Performance: inefficient algorithms, missing caching, unbounded queries
           - Style: naming consistency, dead code, complexity
           - Tests: whether new code paths have corresponding tests
        4. Produce a structured review.

        Output format:
        ## PR Summary
        - Title, author, and one-sentence purpose

        ## Findings
        For each finding:
        - [CRITICAL / WARNING / INFO] File: <path> Line: <line>
          Description and suggested fix

        ## Verdict
        - APPROVE, REQUEST CHANGES, or NEEDS DISCUSSION
        - One-paragraph rationale

        ## Items Needing Your Attention
        - Numbered list of the most important items the maintainer should look at
        """,
        agent=agent,
        expected_output="Structured PR review with severity-labeled findings and a clear verdict",
    )
