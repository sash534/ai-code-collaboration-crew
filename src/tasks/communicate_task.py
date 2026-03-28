from crewai import Task


def create_communicate_task(agent, service: str, detect_task, analyze_task, triage_task):
    return Task(
        description=(
            f"Create an incident ticket and notify the team about the '{service}' incident.\n\n"
            "Steps:\n"
            "1. Create a Jira incident ticket with:\n"
            "   - Summary: '[SEV-X] <service> — <one-line description>'\n"
            "   - Description: Include severity, root cause, impact, affected endpoints, "
            "and timeline from the previous analysis\n"
            "   - Priority: Map from severity (SEV-1→Critical, SEV-2→High, SEV-3→Medium, SEV-4→Low)\n"
            "   - Labels: include the service name and severity\n"
            "2. Send a Slack notification to the 'incident-response' channel with:\n"
            "   - Severity level\n"
            "   - Affected service\n"
            "   - Impact summary (user count)\n"
            "   - Root cause one-liner\n"
            "   - Jira ticket ID\n"
            "   - Current status: 'Investigating'"
        ),
        expected_output=(
            "Confirmation of:\n"
            "- Jira ticket creation (include ticket ID and key)\n"
            "- Slack notification sent (include channel and message summary)"
        ),
        agent=agent,
        context=[detect_task, analyze_task, triage_task],
    )
