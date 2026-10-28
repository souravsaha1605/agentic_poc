"""Review Azure changes with what-if; deploy only with explicit --execute.

Run from an authenticated Azure CLI/Cloud Shell. The OpenAI API key alone cannot
provision Azure resources. This script never grants Databricks data access or
turns on Teams/LLM flags; those require separate validated release gates.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

if __package__:
    from .build_web_package import build
else:
    from build_web_package import build


def run(arguments, capture=False):
    # Never include secret values in the argument list or echo command output.
    result = subprocess.run(
        [
            "az",
            *arguments,
            "--only-show-errors",
            "--output",
            "json" if capture else "none",
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(
            "Azure CLI operation failed: "
            + arguments[0]
            + " "
            + arguments[1]
            + ". Inspect Azure activity/deployment logs securely."
        )
    if not capture:
        return None
    # Some Azure CLI versions render a successful what-if without returning a
    # JSON document on stdout. Treat that as a successful empty result instead
    # of hiding the real outcome behind JSONDecodeError.
    return json.loads(result.stdout) if result.stdout.strip() else {}


def deploy(args):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,49}", args.app_name):
        raise ValueError("Invalid app name.")
    if not re.fullmatch(r"[a-z0-9]{3,24}", args.storage_name):
        raise ValueError("Storage names require 3..24 lowercase letters/digits.")
    account = run(
        ["account", "show", "--subscription", args.subscription], capture=True
    )
    if not account.get("id"):
        raise RuntimeError("An authenticated Azure subscription is required.")
    template = Path(__file__).with_name("azuredeploy.json")
    parameters = [
        "appName=" + args.app_name,
        "storageName=" + args.storage_name,
        "location=" + args.location,
        "database=" + args.database,
    ]
    common = [
        "--subscription",
        args.subscription,
        "--resource-group",
        args.resource_group,
        "--template-file",
        str(template),
        "--parameters",
        *parameters,
    ]
    if not args.execute:
        # What-if details contain resource names and SKUs, never OpenAI credentials.
        preview = run(["deployment", "group", "what-if", *common], capture=True)
        print(json.dumps(preview, indent=2))
        return
    run(
        [
            "group",
            "create",
            "--subscription",
            args.subscription,
            "--name",
            args.resource_group,
            "--location",
            args.location,
        ]
    )
    run(["deployment", "group", "create", *common])
    with tempfile.TemporaryDirectory(prefix="forecast-azure-deploy-") as folder:
        private_files = {}
        for name, source in [
            ("identity-map.json", args.identity_map),
            ("privacy.txt", args.privacy_notice),
            ("terms.txt", args.terms_notice),
            ("acceptance-gates.json", args.acceptance_report),
        ]:
            if source:
                private_files[name] = Path(source)
        package = build(Path(folder) / "app.zip", private_files)
        run(
            [
                "webapp",
                "deploy",
                "--subscription",
                args.subscription,
                "--resource-group",
                args.resource_group,
                "--name",
                args.app_name,
                "--src-path",
                str(package),
                "--type",
                "zip",
            ]
        )
    print(
        "Deployed with Teams and LLM disabled. Configure trusted identity, Databricks grants and secure settings, then run release gates."
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in (
        "subscription",
        "resource-group",
        "location",
        "app-name",
        "storage-name",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--database", default="workspace.forecast_rca_lab")
    for name in ("identity-map", "privacy-notice", "terms-notice", "acceptance-report"):
        p.add_argument("--" + name)
    p.add_argument(
        "--execute",
        action="store_true",
        help="Apply reviewed changes; provisions paid B1 hosting and storage.",
    )
    deploy(p.parse_args())
