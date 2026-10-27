"""Small opt-in Azure check: at most three TOTAL ledger attempts for validation.

Run only after endpoint egress is allowed. This script fails on provider errors;
it never turns a deterministic fallback into a claimed live-model success.
Only a compact synthetic aggregate is sent, and automatic retries stay disabled.
"""

import argparse
import json
from pathlib import Path
from client import get_client, runtime_setting
from cost_control import CallBudget, EvidenceSelector
from lab import local_provider, GLOBAL, END
from business import BusinessService
from contracts import AnalysisPlan


def validate(state_dir, report_path, max_attempts=3):
    budget = CallBudget(Path(state_dir) / "paid-calls.sqlite3")
    limit = min(3, max(0, int(max_attempts)))
    report = {
        "paid_attempts_before": budget.used,
        "validation_total_attempt_limit": limit,
        "checks": [],
    }
    selector = EvidenceSelector(
        get_client(), runtime_setting("AZURE_OPENAI_DEPLOYMENT"), budget
    )
    service = BusinessService(local_provider(), today=END)
    for tool in ("get_forecast_context", "get_revenue_context"):
        if budget.used >= limit:
            break
        evidence = service.execute(
            AnalysisPlan(
                tool=tool, product_id="P0001", region="North", category="Dairy"
            ),
            GLOBAL,
        )
        facts = {
            "scope": evidence["entity"],
            "period": evidence["period"],
            "result": evidence.get("metrics")
            or {
                "gross_revenue": evidence["gross_revenue"],
                "net_revenue": evidence["net_revenue"],
                "currency": evidence["currency"],
            },
        }
        check = {"tool": tool}
        try:
            selected = selector.select(facts)
            check.update(success=True, selected_ids=selected, usage=selector.last_usage)
        except Exception as exc:
            check.update(
                success=False,
                error_type=type(exc).__name__,
                http_status=getattr(exc, "status_code", None),
            )
        report["checks"].append(check)
        if not check["success"]:
            break  # No unchanged retries after a failed request.
    report["paid_attempts_after"] = budget.used
    report["success"] = bool(report["checks"]) and all(
        c["success"] for c in report["checks"]
    )
    Path(report_path).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report["success"]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state-dir", default=str(Path(__file__).parent / ".rca_state"))
    p.add_argument("--report", required=True)
    p.add_argument("--max-attempts", type=int, default=3)
    args = p.parse_args()
    raise SystemExit(
        0 if validate(args.state_dir, args.report, args.max_attempts) else 1
    )
