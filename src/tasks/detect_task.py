from crewai import Task


def create_detect_task(agent, service: str):
    return Task(
        description=(
            f"Investigate a potential production incident affecting the '{service}' service.\n\n"
            "Steps:\n"
            "1. Check active alerts to see what triggered this investigation\n"
            "2. Search for error logs from the affected service\n"
            "3. Check API endpoint error rates to identify which endpoints are failing\n\n"
            "Compile your findings into a structured incident signal."
        ),
        expected_output=(
            "A structured incident signal containing:\n"
            "- Affected service name\n"
            "- Error type and message (the most common error)\n"
            "- Error rate (errors per minute)\n"
            "- Affected endpoints\n"
            "- Time window (when errors started)\n"
            "- Initial severity estimate"
        ),
        agent=agent,
    )
