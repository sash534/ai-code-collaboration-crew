from crewai import Task


def create_triage_task(agent, service: str, detect_task, analyze_task):
    return Task(
        description=(
            f"Classify the severity and assess the blast radius of the '{service}' incident.\n\n"
            "Steps:\n"
            "1. Check host health status to see how many hosts are affected\n"
            "2. Review the error rates and affected user count from previous analysis\n"
            "3. Classify severity using this framework:\n"
            "   - SEV-1: Revenue-impacting or all-users-affected\n"
            "   - SEV-2: Data integrity issues or major feature degradation\n"
            "   - SEV-3: Non-critical degradation, workaround exists\n"
            "   - SEV-4: Minor issue, no user-facing impact\n"
            "4. Recommend immediate response actions"
        ),
        expected_output=(
            "A triage report containing:\n"
            "- Severity level (SEV-1 through SEV-4) with justification\n"
            "- Blast radius: number of affected hosts (healthy vs degraded vs critical)\n"
            "- Estimated affected users\n"
            "- Business impact summary\n"
            "- Recommended immediate actions (e.g., rollback, page on-call, scale up)"
        ),
        agent=agent,
        context=[detect_task, analyze_task],
    )
