#!/usr/bin/env python3
"""Summarize JSON Lines HTTP access logs with explicit quality and SLO signals."""

import argparse
from collections import Counter
from datetime import datetime, timedelta
import json
import math
from pathlib import Path
import sys
from typing import Iterable, TextIO


def _new_bucket() -> dict[str, object]:
    return {"requests": 0, "server_errors_5xx": 0, "client_errors_4xx": 0, "latencies": []}


def _bucket_report(bucket: dict[str, object]) -> dict[str, object]:
    latencies = sorted(bucket["latencies"])
    report = {key: value for key, value in bucket.items() if key != "latencies"}
    requests = int(report["requests"])
    server_errors = int(report["server_errors_5xx"])
    report["server_error_rate_percent"] = round(
        100 * server_errors / requests, 2
    ) if requests else 0.0
    report["p95_latency_ms"] = (
        latencies[math.ceil(0.95 * len(latencies)) - 1] if latencies else None
    )
    return report


def summarize(lines: Iterable[str]) -> dict[str, object]:
    requests = 0
    server_errors = 0
    client_errors = 0
    malformed_lines = 0
    latencies: list[float] = []
    route_counts: Counter[str] = Counter()
    release_buckets: dict[str, dict[str, object]] = {}
    minute_buckets: dict[str, dict[str, object]] = {}

    for line in lines:
        try:
            record = json.loads(line)
            schema_version = record["schema_version"]
            service = record["service"]
            environment = record["environment"]
            release = record["release"]
            status = record["status"]
            latency = record["latency_ms"]
            path = record["path"]
            method = record["method"]
            timestamp = record["timestamp"]
            if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
                raise ValueError("timestamp must be an ISO 8601 UTC string ending in Z")
            parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if (
                type(schema_version) is not int
                or schema_version != 1
                or not isinstance(service, str)
                or not service
                or not isinstance(environment, str)
                or not environment
                or not isinstance(release, str)
                or not release
                or not isinstance(record["request_id"], str)
                or not record["request_id"]
                or not isinstance(record["trace_id"], str)
                or not record["trace_id"]
                or parsed_timestamp.utcoffset() != timedelta(0)
                or isinstance(status, bool)
                or not isinstance(status, int)
                or status < 100
                or status > 599
                or isinstance(latency, bool)
                or not isinstance(latency, (int, float))
                or not math.isfinite(latency)
                or latency < 0
                or not isinstance(path, str)
                or not path.startswith("/")
                or not isinstance(method, str)
                or not method
                or not isinstance(timestamp, str)
                or not timestamp
            ):
                raise ValueError("invalid record fields")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            malformed_lines += 1
            continue

        requests += 1
        server_errors += 500 <= status <= 599
        client_errors += 400 <= status <= 499
        latencies.append(float(latency))
        route_counts[path] += 1
        minute = parsed_timestamp.replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        for buckets, key in (
            (minute_buckets, minute),
            (release_buckets, release),
        ):
            bucket = buckets.setdefault(key, _new_bucket())
            bucket["requests"] += 1
            bucket["server_errors_5xx"] += 500 <= status <= 599
            bucket["client_errors_4xx"] += 400 <= status <= 499
            bucket["latencies"].append(float(latency))

    latencies.sort()
    p95_latency_ms = None
    if latencies:
        nearest_rank = math.ceil(0.95 * len(latencies))
        p95_latency_ms = latencies[nearest_rank - 1]

    error_rate = (100 * server_errors / requests) if requests else 0.0
    top_routes = [
        {"path": path, "requests": count}
        for path, count in sorted(route_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
    ]
    by_release = [
        {"release": release, **_bucket_report(bucket)}
        for release, bucket in sorted(release_buckets.items())
    ]
    time_buckets_1m = [
        {"minute_utc": minute, **_bucket_report(bucket)}
        for minute, bucket in sorted(minute_buckets.items())
    ]
    return {
        "requests": requests,
        "server_errors_5xx": server_errors,
        "client_errors_4xx": client_errors,
        "server_error_rate_percent": round(error_rate, 2),
        "p95_latency_ms": p95_latency_ms,
        "malformed_lines": malformed_lines,
        "top_routes": top_routes,
        "by_release": by_release,
        "time_buckets_1m": time_buckets_1m,
    }


def write_report(report: dict[str, object], stream: TextIO) -> None:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logfile", type=Path, help="JSON Lines access log")
    parser.add_argument(
        "--max-5xx-rate",
        type=float,
        default=5.0,
        help="maximum allowed 5xx percentage before returning exit code 1 (default: 5)",
    )
    args = parser.parse_args()
    if not 0 <= args.max_5xx_rate <= 100:
        parser.error("--max-5xx-rate must be between 0 and 100")

    try:
        with args.logfile.open(encoding="utf-8") as logfile:
            report = summarize(logfile)
    except OSError as error:
        print(f"cannot read {args.logfile}: {error}", file=sys.stderr)
        return 2

    write_report(report, sys.stdout)
    if report["requests"] == 0 or report["malformed_lines"]:
        return 2
    if report["server_error_rate_percent"] > args.max_5xx_rate:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())