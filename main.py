import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

SCENARIOS = {
    "payment_outage": "payment-svc",
    "auth_failure": "auth-svc",
    "database_corruption": "user-profile-svc",
}


def run_code_collab(feature: str):
    from src.crew import build_crew

    crew = build_crew(feature)
    result = crew.kickoff()
    print("\n=== FINAL OUTPUT ===\n")
    print(result)


def load_scenario_into_mocks(scenario: str):
    """Tell mock services to load the scenario fixture data."""
    import httpx

    for port in [8001, 8004]:
        url = f"http://localhost:{port}/api/scenario/load?name={scenario}"
        try:
            resp = httpx.post(url, timeout=5.0)
            data = resp.json()
            if "error" in data:
                print(f"  Warning: {data['error']}")
            else:
                print(f"  Loaded scenario on port {port}")
        except httpx.ConnectError:
            print(f"  Error: Cannot connect to mock service on port {port}.")
            print(f"  Make sure mock services are running: python mock_services/run_all.py")
            sys.exit(1)


def run_incident_response(scenario: str, service: str):
    from src.incident_crew import build_incident_crew

    print(f"\n{'='*60}")
    print(f"  AI INCIDENT RESPONDER")
    print(f"  Scenario: {scenario}")
    print(f"  Service:  {service}")
    print(f"{'='*60}\n")

    print("Loading scenario into mock services...")
    load_scenario_into_mocks(scenario)

    print("\nStarting incident response crew...\n")
    crew = build_incident_crew(service)
    result = crew.kickoff()

    print(f"\n{'='*60}")
    print("  INCIDENT RESPONSE COMPLETE")
    print(f"{'='*60}\n")
    print(result)


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Collaboration & Incident Response Crew",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Code collaboration:\n"
            '    python main.py --feature "Create a function to validate email addresses"\n\n'
            "  Incident response:\n"
            "    python main.py --incident --scenario payment_outage\n"
            "    python main.py --incident --scenario auth_failure\n"
            "    python main.py --incident --scenario database_corruption\n"
            "    python main.py --incident --scenario payment_outage --service payment-svc\n"
        ),
    )

    parser.add_argument("--feature", type=str, help="Feature request for code generation")
    parser.add_argument("--incident", action="store_true", help="Run incident response mode")
    parser.add_argument(
        "--scenario",
        type=str,
        choices=list(SCENARIOS.keys()),
        help="Incident scenario to load (payment_outage, auth_failure, database_corruption)",
    )
    parser.add_argument("--service", type=str, help="Override the affected service name")

    args = parser.parse_args()

    if args.incident:
        if not args.scenario:
            parser.error("--scenario is required when using --incident mode")
        service = args.service or SCENARIOS.get(args.scenario, "unknown-svc")
        run_incident_response(args.scenario, service)
    elif args.feature:
        run_code_collab(args.feature)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
