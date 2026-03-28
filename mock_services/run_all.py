"""Launch all mock services and optionally pre-load a scenario."""

import argparse
import subprocess
import sys
import time
import signal
import os

SERVICES = [
    {"name": "Splunk Mock",  "module": "mock_services.splunk_mock.app:app",  "port": 8001},
    {"name": "Jira Mock",    "module": "mock_services.jira_mock.app:app",    "port": 8002},
    {"name": "Slack Mock",   "module": "mock_services.slack_mock.app:app",   "port": 8003},
    {"name": "GitHub Mock",  "module": "mock_services.github_mock.app:app",  "port": 8004},
    {"name": "GDrive Mock",  "module": "mock_services.gdrive_mock.app:app",  "port": 8005},
]

processes: list[subprocess.Popen] = []


def shutdown(sig=None, frame=None):
    print("\nShutting down mock services...")
    for p in processes:
        p.terminate()
    for p in processes:
        p.wait(timeout=5)
    print("All services stopped.")
    sys.exit(0)


def load_scenario(scenario_name: str):
    """Tell Splunk and GitHub mocks to load a scenario's fixture data."""
    import httpx

    for port in [8001, 8004]:
        url = f"http://localhost:{port}/api/scenario/load?name={scenario_name}"
        try:
            resp = httpx.post(url)
            print(f"  Loaded scenario on port {port}: {resp.json()}")
        except Exception as e:
            print(f"  Failed to load scenario on port {port}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Launch all mock services")
    parser.add_argument("--scenario", type=str, help="Pre-load a scenario (payment_outage, auth_failure, database_corruption)")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("Starting mock services...")
    for svc in SERVICES:
        cmd = [sys.executable, "-m", "uvicorn", svc["module"], "--port", str(svc["port"]), "--host", "0.0.0.0"]
        p = subprocess.Popen(cmd, cwd=project_root)
        processes.append(p)
        print(f"  {svc['name']} starting on port {svc['port']} (PID {p.pid})")

    time.sleep(3)

    if args.scenario:
        print(f"\nLoading scenario: {args.scenario}")
        load_scenario(args.scenario)

    print("\nAll mock services running. Press Ctrl+C to stop.\n")
    print("Service endpoints:")
    for svc in SERVICES:
        print(f"  {svc['name']:15s}  http://localhost:{svc['port']}/api/health")

    for p in processes:
        p.wait()


if __name__ == "__main__":
    main()
