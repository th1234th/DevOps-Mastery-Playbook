import json
from pathlib import Path
import sys
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analyze_access_log import summarize


class SummarizeAccessLogTests(unittest.TestCase):
    def make_record(self, **overrides):
        record = {
            "schema_version": 1,
            "timestamp": "2026-10-25T10:00:00Z",
            "service": "checkout-api",
            "environment": "production-synthetic",
            "release": "2026.10.25.1",
            "request_id": "synthetic-req-test",
            "trace_id": "synthetic-trace-test",
            "method": "GET",
            "path": "/health",
            "status": 200,
            "latency_ms": 10,
        }
        record.update(overrides)
        return record

    def test_counts_errors_p95_and_routes(self):
        fixture = SCRIPT_DIR.parent / "fixtures" / "access.jsonl"
        with fixture.open(encoding="utf-8") as access_log:
            report = summarize(access_log)

        self.assertEqual(report["requests"], 600)
        self.assertEqual(report["server_errors_5xx"], 36)
        self.assertEqual(report["client_errors_4xx"], 3)
        self.assertEqual(report["server_error_rate_percent"], 6.0)
        self.assertEqual(report["p95_latency_ms"], 1025.0)
        self.assertEqual(report["malformed_lines"], 0)
        self.assertEqual(report["top_routes"][0], {"path": "/checkout", "requests": 180})
        self.assertEqual(len(report["time_buckets_1m"]), 10)
        self.assertEqual(report["by_release"][0]["server_error_rate_percent"], 0.0)
        self.assertEqual(report["by_release"][1]["server_error_rate_percent"], 30.0)
        self.assertEqual(report["time_buckets_1m"][-2]["minute_utc"], "2026-10-25T10:08:00Z")
        self.assertEqual(report["time_buckets_1m"][-2]["server_errors_5xx"], 18)

    def test_invalid_json_is_counted_without_crashing(self):
        valid = json.dumps(self.make_record())
        report = summarize([valid, "{not-json}\n"])

        self.assertEqual(report["requests"], 1)
        self.assertEqual(report["malformed_lines"], 1)

    def test_boolean_status_is_not_accepted_as_integer(self):
        report = summarize(
            [
                json.dumps(
                    self.make_record(status=True)
                )
            ]
        )

        self.assertEqual(report["requests"], 0)
        self.assertEqual(report["malformed_lines"], 1)

    def test_non_utc_timestamp_is_rejected(self):
        report = summarize([json.dumps(self.make_record(timestamp="2026-10-25T10:00:00+01:00"))])

        self.assertEqual(report["requests"], 0)
        self.assertEqual(report["malformed_lines"], 1)

    def test_unknown_schema_version_is_rejected(self):
        report = summarize([json.dumps(self.make_record(schema_version=2))])

        self.assertEqual(report["requests"], 0)
        self.assertEqual(report["malformed_lines"], 1)


if __name__ == "__main__":
    unittest.main()