"""Beginner-friendly CLI. Default validation performs ZERO paid API calls."""

import argparse
import getpass
import os
import sys
import unittest
from pathlib import Path
from contracts import Principal
from runtime import create_core
from agents.forecast_rca_agent import ForecastIntelligenceAgent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--session", default="local-development")
    parser.add_argument("--backend", choices=["lab", "spark"], default="lab")
    args = parser.parse_args()
    if not args.interactive:
        suite = unittest.defaultTestLoader.discover(
            str(Path(__file__).parent / "tests")
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    # Local OS identity is acceptable only in the development harness. Teams
    # derives tenant/object IDs from validated SDK activity, never CLI arguments.
    principal = Principal(
        tenant="local-development",
        subject=getpass.getuser(),
        regions=("*",)
        if args.backend == "lab"
        else tuple(filter(None, os.getenv("FORECAST_ALLOWED_REGIONS", "").split(","))),
        products=("*",)
        if args.backend == "lab"
        else tuple(filter(None, os.getenv("FORECAST_ALLOWED_PRODUCTS", "").split(","))),
        categories=("*",)
        if args.backend == "lab"
        else tuple(
            filter(None, os.getenv("FORECAST_ALLOWED_CATEGORIES", "").split(","))
        ),
    )
    core = create_core(args.backend)
    agent = ForecastIntelligenceAgent(core, principal, args.session)
    print(
        "Forecast RCA | " + args.backend + " | LLM " + os.getenv("ENABLE_LLM", "false")
    )
    print("Use the same --session after restarting. Type exit to stop.")
    while True:
        try:
            message = input("You: ").strip()
        except EOFError:
            break
        if message.lower() in ("exit", "quit"):
            break
        if not message:
            continue
        try:
            print(agent.run(message).response)
        except (ValueError, PermissionError, RuntimeError):
            print(
                "The turn could not be completed. Check the scope, data readiness and service configuration; no result was fabricated."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
