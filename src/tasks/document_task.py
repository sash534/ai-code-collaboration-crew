from crewai import Task


def create_document_task(agent, service: str, detect_task, analyze_task, triage_task, communicate_task, remediate_task):
    return Task(
        description=(
            f"Create a comprehensive post-incident report for the '{service}' incident.\n\n"
            "Compile all information from the previous phases into a structured document:\n\n"
            "1. **Executive Summary** — One paragraph: what happened, severity, impact, resolution\n"
            "2. **Timeline** — Chronological events from first deploy/change through detection, "
            "investigation, notification, and remediation\n"
            "3. **Root Cause Analysis** — Technical details of what went wrong, which code/config "
            "change caused it, and why it wasn't caught earlier\n"
            "4. **Impact Assessment** — Number of affected users, affected endpoints, duration "
            "of impact, business impact (revenue, data, reputation)\n"
            "5. **Remediation** — What was done to fix it (PR created, rollback, config revert), "
            "current status\n"
            "6. **Action Items** — Follow-up tasks to prevent recurrence:\n"
            "   - Add null-safety checks / input validation\n"
            "   - Improve test coverage for the affected code path\n"
            "   - Add monitoring/alerting for earlier detection\n"
            "   - Review deployment/change processes\n\n"
            "Create the report as a document with a descriptive title including the date and service name."
        ),
        expected_output=(
            "Confirmation that the post-incident report document was created, including:\n"
            "- Document title\n"
            "- Document URL/ID\n"
            "- Summary of what the report contains"
        ),
        agent=agent,
        context=[detect_task, analyze_task, triage_task, communicate_task, remediate_task],
    )
