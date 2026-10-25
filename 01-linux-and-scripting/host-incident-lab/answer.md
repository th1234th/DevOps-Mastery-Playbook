# Host Incident Response Lab: Answer Key

## Expected report

Run:

```sh
python3 01-linux-and-scripting/host-incident-lab/scripts/analyze_access_log.py \
  01-linux-and-scripting/host-incident-lab/fixtures/access.jsonl \
  --max-5xx-rate 5
```

The report is:

```json
{
  "client_errors_4xx": 3,
  "malformed_lines": 0,
  "p95_latency_ms": 1025.0,
  "requests": 600,
  "server_error_rate_percent": 6.0,
  "server_errors_5xx": 36,
  "top_routes": [
    {"path": "/checkout", "requests": 180},
    {"path": "/", "requests": 120},
    {"path": "/catalog", "requests": 120},
    {"path": "/search", "requests": 120},
    {"path": "/health", "requests": 60}
  ]
}
```

The process exits `1` because the aggregate 6% 5xx rate exceeds the 5% threshold. The three 404 responses are client errors and are not counted as server failures. `/checkout` is 30% of the requests (`180/600`). Overall nearest-rank p95 selects sorted position `ceil(0.95 * 600) = 570`, which is 1025 ms.

The report's release comparison is the most useful incident signal:

| Release | Requests | 5xx | 5xx rate | p95 |
| --- | ---: | ---: | ---: | ---: |
| `2026.10.25.1` | 480 | 0 | 0% | 191 ms |
| `2026.10.25.2` | 120 | 36 | 30% | 1725 ms |

The final minute buckets are `10:08Z` and `10:09Z`; each has 60 requests, 18 5xx responses (30%), and p95 latency of 1725 ms. Each is consistent with the `.2` release window. This is strong correlation in a designed exercise, not proof that the release is the cause. A real incident still needs deploy evidence and correlated application/dependency telemetry.

The generator uses a fixed start time and deterministic route/status/latency patterns so every run yields the same 600 records. `schema_version` is `1`; timestamps are UTC ISO 8601 ending in `Z`; route, release, service, environment, and dependency values come from a small bounded set. Client IPs are from `192.0.2.0/24`, reserved for documentation. Request and trace IDs are synthetic identifiers and intentionally should not become Prometheus labels because unique IDs create unbounded time-series cardinality.

## Input quality behavior

After appending `{not-json}`, the analyzer still emits a JSON report with `malformed_lines: 1` and exits `2`. Malformed input takes precedence over the error-rate threshold because the report cannot be trusted as a complete, valid measurement. The analyzer ignores invalid records for counts but makes the data-quality failure explicit.

The tests should report five passing cases: expected aggregate and release/minute statistics, malformed JSON accounting, rejection of boolean `status` (Python treats `bool` as an `int` subclass, so the parser explicitly excludes it), rejection of timestamps that are not UTC `Z` values, and rejection of unsupported schema versions.

## Interpretation and next checks

Observed facts: the fixture has 600 valid requests over 10 minutes, 36 5xx responses (6%), three 4xx responses, and an overall p95 of 1025 ms. The first eight minutes use release `.1` with no 5xx errors; the last two use `.2` with 30% 5xx and 1725 ms p95. The dependency label is `payments-synthetic`, and its latency rises during the degraded window. These fields suggest where to investigate but do not establish why checkout failed. Next request a time-correlated deployment/change record, application exception logs, real dependency health and latency, request traces, and CPU/memory/connection-pool saturation.

`df` reports filesystem-level used/available capacity for the mount containing a path. `du` totals directory entries reachable from a directory. They can differ due to deleted-but-open files, mount boundaries, sparse files, permissions, reserved blocks, and filesystem metadata. On a real host, identify the mount with `findmnt -T <path>`, compare `df -hT` with `du -xhd1 <mount>`, and investigate deleted-open files with an approved tool such as `lsof +L1`. Do not kill processes or remove logs merely to make the numbers match.

## Example Incident Note

**Service/window:** Synthetic checkout API, 2026-10-25 10:00Z-10:10Z, 600 requests at one request per second. This deterministic fixture is for training; its volume and distribution do not define a production alert policy.

**Impact signal:** 36/600 requests returned 5xx (6%), exceeding the lab's 5% threshold. Aggregate p95 was 1025 ms. In the final two minutes, 36/120 requests returned 5xx (30%) and p95 was 1725 ms. All synthetic 5xx responses were on `/checkout`.

**Host checks:** Record actual `df`, `du`, process, memory, and mount observations from the exercise. No host service or system log was changed.

**Hypotheses:** The regression begins at the same time as synthetic release `.2`, and `payments-synthetic` latency is elevated. A dependency timeout or an application/configuration change could explain the route-specific failures; neither is proven by this generated log. Request application errors, dependency metrics, traces, and deployment history.

**Mitigation/recovery:** Follow the service runbook. Consider rollback only after checking change correlation and rollback safety. Preserve logs and confirm the error rate and latency recover after any action.

**Follow-up:** Owner, next update time, evidence request, and verification window. Keep observations distinct from hypotheses.

## Production Caveats

The sample analyzer is an educational starting point, not an on-host monitoring agent. A production implementation should define schema evolution, timestamp/time-zone policy, redaction and retention, streaming/large-file behavior, alert windows and minimum sample counts, bounded cardinality, and integration with the service's real SLO. The fixture contains no real customer data; never put real request IDs, trace IDs, addresses, credentials, or secrets in committed fixtures or reports. Keep unique IDs in logs/traces for correlation, not as metric labels.
