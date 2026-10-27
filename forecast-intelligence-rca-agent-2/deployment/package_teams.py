"""Create a personal Teams app ZIP after the real bot registration exists.

This only writes a local package; it neither installs the app nor enables Teams.
Example:
 python deployment/package_teams.py --app-id UUID --bot-id UUID \
   --host https://your-app.azurewebsites.net --output /tmp/forecast-teams.zip
"""

import argparse
import binascii
import json
import struct
import uuid
import zlib
from urllib.parse import urlsplit
from zipfile import ZipFile


def icon(size, outline=False):
    """Small original F icon, using only Python's standard PNG encoding tools."""
    pixels = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            x_ratio, y_ratio = x / size, y / size
            letter = (
                0.27 <= x_ratio <= 0.40
                and 0.2 <= y_ratio <= 0.8
                or 0.27 <= x_ratio <= 0.74
                and 0.2 <= y_ratio <= 0.33
                or 0.27 <= x_ratio <= 0.65
                and 0.43 <= y_ratio <= 0.56
            )
            row.extend(
                (255, 255, 255, 255)
                if letter
                else (0, 0, 0, 0)
                if outline
                else (20, 65, 110, 255)
            )
        pixels.append(b"\x00" + row)

    def chunk(kind, data):
        return (
            struct.pack("!I", len(data))
            + kind
            + data
            + struct.pack("!I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack("!2I5B", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"".join(pixels)))
        + chunk(b"IEND", b"")
    )


def package(app_id, bot_id, host, output):
    app_id, bot_id = str(uuid.UUID(app_id)), str(uuid.UUID(bot_id))
    parsed = urlsplit(host)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use the actual public HTTPS app origin.")
    host = host.rstrip("/")
    manifest = {
        "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.19/MicrosoftTeams.schema.json",
        "manifestVersion": "1.19",
        "version": "1.0.0",
        "id": app_id,
        "packageName": "com.forecast.rca",
        "developer": {
            "name": "Forecast RCA project",
            "websiteUrl": host,
            "privacyUrl": host + "/privacy",
            "termsOfUseUrl": host + "/terms",
        },
        "name": {
            "short": "Forecast RCA",
            "full": "Forecast Intelligence and RCA Agent",
        },
        "description": {
            "short": "Read-only forecast and supply-chain investigations.",
            "full": "User-owned forecast, revenue, inventory and root-cause investigations with deterministic evidence and saved case versions.",
        },
        "icons": {"color": "color.png", "outline": "outline.png"},
        "accentColor": "#14416E",
        "bots": [
            {
                "botId": bot_id,
                "scopes": ["personal"],
                "supportsFiles": False,
                "isNotificationOnly": False,
            }
        ],
        "permissions": ["identity", "messageTeamMembers"],
        "validDomains": [parsed.hostname],
    }
    with ZipFile(output, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        archive.writestr("color.png", icon(192))
        archive.writestr("outline.png", icon(32, outline=True))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--bot-id", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    package(args.app_id, args.bot_id, args.host, args.output)
    print("Wrote Teams package. Tenant validation and installation are still required.")
