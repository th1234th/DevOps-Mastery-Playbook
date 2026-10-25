#!/usr/bin/env python3
"""Generate deterministic, privacy-safe synthetic checkout access logs."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys


REQUEST_COUNT = 600
INCIDENT_START = datetime(2026, 10, 25, 10, 8, tzinfo=timezone.utc)
ROUTE_PATTERN = (
    "/checkout",
    "/checkout",
    "/catalog",
    "/search",
    "/",
    "/health",
    "/checkout",
    "/catalog",
    "/search",
    "/",
)
USER_AGENT_FAMILIES = ("SyntheticWeb/1.0", "SyntheticMobile/1.0", "SyntheticBot/1.0")


def records():
    start = datetime(2026, 10, 25, 10, 0, tzinfo=timezone.utc)
    for index in range(REQUEST_COUNT):
        timestamp = start + timedelta(seconds=index)
        path = ROUTE_PATTERN[index % len(ROUTE_PATTERN)]
        incident = timestamp >= INCIDENT_START and path == "/checkout"
        status = 503 if incident else 200
        if path == "/search" and index % 53 == 0:
            status = 404

        if incident:
            latency_ms = 850 + (index % 7) * 175
        elif path == "/health":
            latency_ms = 8 + index % 8
        else:
            latency_ms = 25 + (index * 37) % 176

        record = {
            "schema_version": 1,
            "timestamp": timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "service": "checkout-api",
            "environment": "production-synthetic",
            "release": "2026.10.25.2" if timestamp >= INCIDENT_START else "2026.10.25.1",
            "request_id": f"synthetic-req-{index + 1:06d}",
            "trace_id": f"synthetic-trace-{index + 1:06d}",
            "client_ip": f"192.0.2.{index % 250 + 1}",
            "user_agent_family": USER_AGENT_FAMILIES[index % len(USER_AGENT_FAMILIES)],
            "method": "POST" if path == "/checkout" else "GET",
            "path": path,
            "status": status,
            "latency_ms": latency_ms,
        }
        if path == "/checkout":
            record["dependency"] = "payments-synthetic"
            record["dependency_latency_ms"] = 700 + index % 9 * 120 if incident else 18 + index % 80
        yield record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="output JSON Lines path")
    args = parser.parse_args()

    try:
        with args.output.open("w", encoding="utf-8", newline="\n") as output:
            for record in records():
                output.write(json.dumps(record, separators=(",", ":"), sort_keys=True))
                output.write("\n")
    except OSError as error:
        print(f"cannot write {args.output}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())