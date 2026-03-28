from crewai import Crew, Process

from src.agents.detector import get_detector
from src.agents.log_analyst import get_log_analyst
from src.agents.triage import get_triage_agent
from src.agents.communicator import get_communicator
from src.agents.remediator import get_remediator
from src.agents.documenter import get_documenter

from src.tasks.detect_task import create_detect_task
from src.tasks.analyze_task import create_analyze_task
from src.tasks.triage_task import create_triage_task
from src.tasks.communicate_task import create_communicate_task
from src.tasks.remediate_task import create_remediate_task
from src.tasks.document_task import create_document_task


def build_incident_crew(service: str) -> Crew:
    """Build the incident response crew for a given service.

    The pipeline: Detect → Analyze → Triage → Communicate → Remediate → Document
    Each task receives context from previous tasks via CrewAI's context parameter.
    """
    detector = get_detector()
    log_analyst = get_log_analyst()
    triage = get_triage_agent()
    communicator = get_communicator()
    remediator = get_remediator()
    documenter = get_documenter()

    detect_task = create_detect_task(detector, service)
    analyze_task = create_analyze_task(log_analyst, service, detect_task)
    triage_task = create_triage_task(triage, service, detect_task, analyze_task)
    communicate_task = create_communicate_task(communicator, service, detect_task, analyze_task, triage_task)
    remediate_task = create_remediate_task(remediator, service, detect_task, analyze_task)
    document_task = create_document_task(documenter, service, detect_task, analyze_task, triage_task, communicate_task, remediate_task)

    return Crew(
        agents=[detector, log_analyst, triage, communicator, remediator, documenter],
        tasks=[detect_task, analyze_task, triage_task, communicate_task, remediate_task, document_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )
