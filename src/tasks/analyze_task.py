from crewai import Task


def create_analyze_task(agent, service: str, detect_task):
    return Task(
        description=(
            f"Perform deep root cause analysis for the incident on '{service}'.\n\n"
            "Steps:\n"
            "1. Get stack traces for the service to identify the exception and code location\n"
            "2. Search logs for deployment events, config changes, or other system events "
            "that correlate with the incident start time\n"
            "3. Check recent deployments to see if a deploy happened shortly before the incident\n"
            "4. Formulate a root cause hypothesis with supporting evidence\n\n"
            "Focus on answering: WHAT is breaking, WHERE in the code, and WHY did it start now?"
        ),
        expected_output=(
            "A root cause analysis containing:\n"
            "- Root cause hypothesis (one sentence)\n"
            "- Exception type and origin (file:line)\n"
            "- Full stack trace of the most common error\n"
            "- Correlated change (deploy commit SHA, config change, etc.)\n"
            "- Timeline: when the change was made vs when errors started\n"
            "- Confidence level (high/medium/low)"
        ),
        agent=agent,
        context=[detect_task],
    )
