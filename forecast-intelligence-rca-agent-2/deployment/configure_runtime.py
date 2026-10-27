"""Merge secure runtime settings after the reviewed Azure resource deployment.

Requires an already authenticated Azure CLI. Values come from process bindings
or explicit non-secret source coordinates; no key is embedded in the repository,
command line or console. Teams and model use are left disabled.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlsplit


def setting(name):
    return os.getenv(name) or os.getenv("MY_" + name)


def configure(args):
    parsed = urlsplit(args.databricks_host)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ValueError("Use an HTTPS Databricks workspace origin.")
    values = {
        "DATABRICKS_HOST": args.databricks_host.rstrip("/"),
        "DATABRICKS_SERVER_HOSTNAME": parsed.hostname,
        "DATABRICKS_HTTP_PATH": args.warehouse_path,
        "DATABRICKS_AZURE_RESOURCE_ID": args.databricks_resource_id,
        "FORECAST_DATABASE": args.database,
        "TEAMS_ENABLED": "false",
        "ENABLE_LLM": "false",
        "GENIE_MODE": "off",
        "CHANNEL_MODE": "development",
    }
    for name in (
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
    ):
        if setting(name):
            values[name] = setting(name)
    with tempfile.TemporaryDirectory(prefix="forecast-private-settings-") as folder:
        path = Path(folder) / "settings.json"
        path.write_text(json.dumps(values))
        path.chmod(0o600)
        result = subprocess.run(
            [
                "az",
                "webapp",
                "config",
                "appsettings",
                "set",
                "--subscription",
                args.subscription,
                "--resource-group",
                args.resource_group,
                "--name",
                args.app_name,
                "--settings",
                "@" + str(path),
                "--only-show-errors",
                "--output",
                "none",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(
                "Runtime configuration failed; inspect Azure logs securely. No secret output was printed."
            )
    print(
        "Merged runtime bindings. Teams/LLM remain disabled until live release gates pass."
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in (
        "subscription",
        "resource-group",
        "app-name",
        "databricks-host",
        "warehouse-path",
        "databricks-resource-id",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--database", default="workspace.forecast_rca_lab")
    configure(p.parse_args())
