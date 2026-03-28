# AI Code Collaboration & Incident Response Crew

A multi-agent AI system built with CrewAI that provides two workflows:

1. **Code Collaboration** — AI agents generate, review, and test code collaboratively
2. **Incident Response** — AI agents detect, triage, diagnose, communicate, remediate, and document production incidents automatically

## Incident Response Architecture

```
Incident Trigger
       │
       ▼
┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│   Detector   │────▶│  Log Analyst  │────▶│   Triage    │
│  (Splunk)    │     │  (Splunk)     │     │  (Splunk)   │
└──────────────┘     └───────────────┘     └──────┬──────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼                           ▼
                            ┌──────────────┐          ┌──────────────┐
                            │ Communicator │          │  Remediator  │
                            │ (Jira+Slack) │          │  (GitHub)    │
                            └──────────────┘          └──────┬───────┘
                                                             │
                                                             ▼
                                                    ┌──────────────┐
                                                    │  Documenter  │
                                                    │ (Google Drive)│
                                                    └──────────────┘
```

Each agent talks to a **mock FastAPI microservice** that simulates the real tool (Splunk, Jira, Slack, GitHub, Google Drive). Swap to real services later by changing environment variables.

## Tech Stack

* **CrewAI** — Multi-agent orchestration
* **FastAPI** — Mock service layer (Splunk, Jira, Slack, GitHub, Google Drive)
* **httpx** — HTTP client for tool-to-service communication
* **Python 3.10+**
* **uv** — Fast dependency manager

## Getting Started

### 1. Install uv

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

### 2. Setup project

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install -e .
```

### 3. Add API Key

Create a `.env` file with your LLM provider key:

```bash
# Option A: Groq (free, fast)
GROQ_API_KEY=your_groq_api_key

# Option B: OpenAI
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run Incident Response

**Terminal 1** — Start mock services:

```bash
python mock_services/run_all.py --scenario payment_outage
```

**Terminal 2** — Run the incident responder:

```bash
python main.py --incident --scenario payment_outage
```

### 5. Run Code Collaboration (original mode)

```bash
python main.py --feature "Create a function to validate email addresses"
```

## Incident Scenarios

Three pre-built scenarios are available:

| Scenario | Service | Root Cause | Severity |
|----------|---------|------------|----------|
| `payment_outage` | payment-svc | NullPointerException after token refactor deploy | SEV-1 |
| `auth_failure` | auth-svc | Redis connection pool reduced from 100 to 5 | SEV-1 |
| `database_corruption` | user-profile-svc | Migration script corrupted 2,300 user rows | SEV-2 |

```bash
python main.py --incident --scenario payment_outage
python main.py --incident --scenario auth_failure
python main.py --incident --scenario database_corruption
```

## Mock Services

Five FastAPI services simulate external tools:

| Service | Port | Endpoints |
|---------|------|-----------|
| Splunk Mock | 8001 | `/api/search/errors`, `/api/stack_traces`, `/api/alerts`, `/api/hosts` |
| Jira Mock | 8002 | `/api/tickets` (CRUD), `/api/search` |
| Slack Mock | 8003 | `/api/messages`, `/api/channels` |
| GitHub Mock | 8004 | `/api/repos/{owner}/{repo}/commits`, `/api/repos/{owner}/{repo}/pulls` |
| GDrive Mock | 8005 | `/api/documents` (CRUD) |

After a run, inspect what the agents did:

```bash
curl http://localhost:8002/api/tickets          # Jira tickets created
curl http://localhost:8003/api/messages          # Slack messages sent
curl http://localhost:8004/api/repos/acme/platform/pulls  # PRs opened
curl http://localhost:8005/api/documents         # Post-incident reports
```

## Swapping to Real Services

Set environment variables to point tools at real APIs:

```bash
SPLUNK_BASE_URL=https://your-splunk-instance:8089/api
JIRA_BASE_URL=https://your-org.atlassian.net/rest/api/3
SLACK_BASE_URL=https://slack.com/api
GITHUB_BASE_URL=https://api.github.com
GDRIVE_BASE_URL=https://www.googleapis.com/drive/v3
```

The CrewAI agents and tools remain unchanged — only the HTTP base URLs change.

## Project Structure

```
├── main.py                     # CLI entry point (--feature or --incident)
├── pyproject.toml              # Dependencies
├── mock_services/
│   ├── run_all.py              # Launch all 5 mock services
│   ├── scenarios/              # JSON fixture data
│   │   ├── payment_outage.json
│   │   ├── auth_failure.json
│   │   └── database_corruption.json
│   ├── splunk_mock/app.py
│   ├── jira_mock/app.py
│   ├── slack_mock/app.py
│   ├── github_mock/app.py
│   └── gdrive_mock/app.py
├── src/
│   ├── config.py               # LLM configuration
│   ├── crew.py                 # Code collaboration crew
│   ├── incident_crew.py        # Incident response crew
│   ├── services/client.py      # HTTP client (configurable base URLs)
│   ├── agents/                 # Agent definitions
│   │   ├── detector.py
│   │   ├── log_analyst.py
│   │   ├── triage.py
│   │   ├── communicator.py
│   │   ├── remediator.py
│   │   └── documenter.py
│   ├── tools/                  # CrewAI tools (HTTP → mock services)
│   │   ├── splunk_tool.py
│   │   ├── jira_tool.py
│   │   ├── slack_tool.py
│   │   ├── github_tool.py
│   │   └── gdrive_tool.py
│   └── tasks/                  # Task definitions
│       ├── detect_task.py
│       ├── analyze_task.py
│       ├── triage_task.py
│       ├── communicate_task.py
│       ├── remediate_task.py
│       └── document_task.py
```
