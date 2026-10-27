"""Build a source-only App Service ZIP without keys, local state or test outputs.

Cloud dependencies become the deployment's requirements.txt so the platform
build installs the Teams SDK as well as the small offline development packages.
"""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse

ROOT = Path(__file__).resolve().parents[1]


def build(output, private_files=None):
    output = Path(output)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        sources = list(ROOT.glob("*.py"))
        for folder in ("agents", "services", "tools", "channels"):
            sources.extend((ROOT / folder).rglob("*.py"))
        for source in sources:
            archive.write(source, source.relative_to(ROOT).as_posix())
        requirements = (
            (ROOT / "requirements.txt").read_text()
            + "\n"
            + "\n".join(
                line
                for line in (ROOT / "requirements-cloud.txt").read_text().splitlines()
                if not line.strip().startswith("-r")
            )
            + "\n"
        )
        archive.writestr("requirements.txt", requirements)
        if private_files:
            allowed = {
                "identity-map.json",
                "privacy.txt",
                "terms.txt",
                "acceptance-gates.json",
            }
            if set(private_files) - allowed:
                raise ValueError("Unknown private deployment file.")
            for name, path in private_files.items():
                archive.write(path, "private/" + name)
    # With real identity/notices included, treat this ZIP as a private artifact.
    output.chmod(0o600)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(build(args.output))
