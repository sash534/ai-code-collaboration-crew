"""Review local git changes using the PR Review Agent.

Runs `git diff` against the base branch, embeds a summarized diff
directly into the task prompt (no GitHub API calls), and produces
a structured code review.

Usage:
    python review_local.py                    # diff against main
    python review_local.py --base origin/main # diff against specific ref
"""

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()

MAX_PATCH_CHARS = 600
MAX_FILES = 15


def get_diff_summary(base: str) -> str:
    result = subprocess.run(
        ["git", "diff", base, "--numstat"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"git diff failed: {result.stderr}")

    files = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        if "egg-info" in path or path.endswith((".json", ".txt", ".md")):
            continue
        files.append((path, int(added) if added != "-" else 0, int(deleted) if deleted != "-" else 0))

    files.sort(key=lambda f: f[1] + f[2], reverse=True)
    files = files[:MAX_FILES]

    sections = []
    for path, added, deleted in files:
        patch = subprocess.run(
            ["git", "diff", base, "--", path],
            capture_output=True, text=True,
        ).stdout
        if len(patch) > MAX_PATCH_CHARS:
            patch = patch[:MAX_PATCH_CHARS] + "\n... (truncated)"
        sections.append(f"### {path}  (+{added}/-{deleted})\n```\n{patch}\n```")

    skipped = max(0, len(result.stdout.strip().splitlines()) - len(sections))
    header = f"Changed files: {len(files)} shown"
    if skipped:
        header += f", {skipped} smaller/non-code files omitted"

    return header + "\n\n" + "\n\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Review local git changes with AI")
    parser.add_argument("--base", default="main", help="Base branch/ref to diff against (default: main)")
    args = parser.parse_args()

    print(f"Collecting diff against '{args.base}' ...")
    diff_summary = get_diff_summary(args.base)

    from crewai import Agent, Crew, Task
    from src.config import get_llm

    reviewer = Agent(
        role="Senior PR Reviewer",
        goal=(
            "Analyze code diffs and flag security vulnerabilities, bugs, "
            "performance regressions, style violations, and missing test coverage."
        ),
        backstory=(
            "You are a principal engineer reviewing code changes. "
            "Classify each finding as Critical, Warning, or Info."
        ),
        allow_delegation=False,
        llm=get_llm(),
        verbose=True,
    )

    task = Task(
        description=f"""
        Review the following code changes and produce a structured review.

        {diff_summary}

        For each file, evaluate:
        - Security: hardcoded secrets, injection risks, unsafe operations
        - Bugs: logic errors, unhandled exceptions, edge cases
        - Performance: inefficient algorithms, unbounded queries
        - Style: naming consistency, dead code, complexity
        - Tests: whether new code has corresponding tests

        Output format:
        ## Summary
        One paragraph describing what these changes do.

        ## Findings
        For each finding:
        - [CRITICAL/WARNING/INFO] File: <path>
          Description and suggested fix

        ## Verdict
        APPROVE, REQUEST CHANGES, or NEEDS DISCUSSION with rationale.

        ## Items Needing Your Attention
        Numbered list of the most important items.
        """,
        agent=reviewer,
        expected_output="Structured code review with severity-labeled findings",
    )

    crew = Crew(agents=[reviewer], tasks=[task], verbose=True, memory=False)

    print("\nRunning review ...\n")
    result = crew.kickoff()

    print("\n=== CODE REVIEW RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()
