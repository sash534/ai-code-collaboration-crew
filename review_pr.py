"""CLI entry point for the PR Review Agent.

Usage:
    python review_pr.py --pr 42
    python review_pr.py --pr 42 --owner sash534 --repo my-repo
    python review_pr.py --pr 42 --mock   # route through local GitHub mock
"""

import argparse
import os

from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Review a GitHub pull request using the AI PR Review Agent"
    )
    parser.add_argument(
        "--pr", type=int, required=True, help="Pull request number to review"
    )
    parser.add_argument(
        "--owner",
        type=str,
        default="sash534",
        help="GitHub repository owner (default: sash534)",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default="ai-code-collaboration-crew",
        help="GitHub repository name (default: ai-code-collaboration-crew)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use local GitHub mock service instead of api.github.com",
    )

    args = parser.parse_args()

    if args.mock:
        os.environ["GITHUB_BASE_URL"] = "http://localhost:8004/api"
        print("Using local GitHub mock at http://localhost:8004")

    from src.pr_review_crew import build_pr_review_crew

    print(f"\nReviewing PR #{args.pr} in {args.owner}/{args.repo} ...\n")

    crew = build_pr_review_crew(args.pr, args.owner, args.repo)
    result = crew.kickoff()

    print("\n=== PR REVIEW RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()
