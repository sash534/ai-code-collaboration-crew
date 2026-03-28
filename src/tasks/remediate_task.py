from crewai import Task


def create_remediate_task(agent, service: str, detect_task, analyze_task):
    return Task(
        description=(
            f"Find the problematic code and create a fix for the '{service}' incident.\n\n"
            "Steps:\n"
            "1. Search the code repository for the file mentioned in the root cause analysis\n"
            "2. List recent commits to identify the one that introduced the bug\n"
            "3. Get the full commit diff to confirm it contains the problematic change\n"
            "4. Create a pull request to revert or fix the issue. The PR should include:\n"
            "   - Title: 'fix: revert/fix <brief description> [INCIDENT]'\n"
            "   - Body: Root cause, what the fix does, link back to the incident\n"
            "   - Head branch: 'hotfix/<service>-incident-fix'"
        ),
        expected_output=(
            "Remediation report containing:\n"
            "- Identified problematic commit (SHA, author, message)\n"
            "- File(s) affected with code diff\n"
            "- Pull request created (URL, title)\n"
            "- Description of the fix"
        ),
        agent=agent,
        context=[detect_task, analyze_task],
    )
