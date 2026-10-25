# Host Incident Response Lab

## Scenario

Checkout latency and server errors are rising just after a deployment. The on-call engineer has a 10-minute JSON Lines access-log capture and a report that the host's log filesystem is growing. Establish scope using read-only Linux tools, measure service impact, compare the release and time windows, distinguish client errors from server errors, validate log quality, and produce an incident note with a safe follow-up plan.

This lab is deliberately local and non-destructive. It never changes host services, permissions, firewall rules, system logs, or real application data. Use only a copied fixture under a temporary directory. The dataset is fictional, deterministic, and contains no real customer records, credentials, or hostnames. Client addresses use the documentation-only `192.0.2.0/24` range; request and trace IDs are synthetic; paths and user-agent values are bounded categories.

The versioned schema uses `schema_version: 1`, ISO 8601 UTC timestamps ending in `Z`, service/environment/release labels, synthetic request and trace IDs, normalized route paths, status, and latency. Checkout rows additionally include a synthetic dependency label and dependency latency. The release changes at `2026-10-25T10:08:00Z`; checkout errors and dependency latency rise in the final two minutes. This creates a testable correlation, not proof that the release caused the incident.

## Prerequisites

- Linux, Bash, Python 3.10+, Git, and core tools: `mktemp`, `cp`, `du`, `df`, `stat`, `wc`, `ps`, `sha256sum`.
- No root access, cloud account, network access, third-party Python packages, or systemd service changes are required.
- Run commands from the repository root. Do not substitute a production log path for the fixture path.

## 1. Create a disposable workspace

Create a unique workspace and copy the provided log. The cleanup guard below only removes a directory created with this exact prefix.

```sh
LAB_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/devops-linux-lab.XXXXXX")"
mkdir -p "$LAB_ROOT/var/log/checkout"
cp 01-linux-and-scripting/host-incident-lab/fixtures/access.jsonl "$LAB_ROOT/var/log/checkout/access.jsonl"
printf 'Lab workspace: %s\n' "$LAB_ROOT"
```

Record the original checksum, file size, line count, and directory usage:

```sh
sha256sum "$LAB_ROOT/var/log/checkout/access.jsonl"
stat "$LAB_ROOT/var/log/checkout/access.jsonl"
wc -l "$LAB_ROOT/var/log/checkout/access.jsonl"
du -sh "$LAB_ROOT"
df -h "$LAB_ROOT"
```

The committed fixture has 600 records, one per second across 10 minutes. Regenerate a copy for comparison or test modifications with:

```sh
python3 01-linux-and-scripting/host-incident-lab/scripts/generate_synthetic_access_log.py \
  "$LAB_ROOT/var/log/checkout/regenerated.jsonl"
```

## 2. Establish host and incident context

These are read-only observations. Capture the current user, kernel, uptime, memory, disk, and the shell's process ancestry. In an actual incident, inspect the affected mount and service process rather than assuming `/` is the full filesystem story.

```sh
id
uname -a
uptime
free -h
df -hT "$LAB_ROOT"
ps -p "$$" -o pid,ppid,stat,comm,args
find "$LAB_ROOT" -type f -printf '%TY-%Tm-%TdT%TH:%TM:%TS %s %p\n' | sort
```

If you have authorized access to a real host, useful read-only checks include `systemctl status <service>`, `journalctl -u <service> --since '30 minutes ago'`, `ss -lntp`, and `ps -eo pid,ppid,stat,%cpu,%mem,comm --sort=-%cpu`. These are reference commands only; this lab does not ask you to change or restart a host service.

## 3. Measure service health from the log

The analyzer reports request count, HTTP 5xx and 4xx counts, 5xx percentage, nearest-rank p95 latency, malformed records, busiest routes, one-minute UTC buckets, and release-level summaries. It validates schema version 1 and UTC timestamps. It returns:

- `0`: valid input and 5xx rate at or below the configured threshold.
- `1`: valid input, but 5xx rate is above the threshold.
- `2`: unreadable/empty input or at least one malformed record.

Run the provided analyzer with a 5% server-error threshold. Exit code `1` is the expected incident signal for this fixture; preserve the JSON report even when the threshold is breached.

```sh
python3 01-linux-and-scripting/host-incident-lab/scripts/analyze_access_log.py \
  "$LAB_ROOT/var/log/checkout/access.jsonl" --max-5xx-rate 5
```

Capture its output to a report file while retaining the exit code:

```sh
set +e
python3 01-linux-and-scripting/host-incident-lab/scripts/analyze_access_log.py \
  "$LAB_ROOT/var/log/checkout/access.jsonl" --max-5xx-rate 5 \
  > "$LAB_ROOT/incident-report.json"
ANALYZER_EXIT=$?
set -e
printf 'Analyzer exit: %s\n' "$ANALYZER_EXIT"
cat "$LAB_ROOT/incident-report.json"
```

Tasks:

1. Compare overall 5xx rate and p95 with release-level and minute-bucket results. State the first minute where the profile changes.
2. Explain why the three `404` responses are 4xx and not server errors. Identify the busiest route and calculate its share of total requests.
3. Explain what the release correlation and `payments-synthetic` dependency latency suggest, and why neither proves root cause. Name the next evidence you would request (application exceptions, dependency health, deploy history, saturation metrics, traces).
4. Identify the privacy and cardinality properties of this schema. Which fields are safe to aggregate, and which should not become Prometheus labels?
5. Explain why `df` and `du` answer different questions and what additional mount-level checks you would perform on a real host.

## 4. Test the input-failure path

Inject a malformed record into the copied workspace, not the committed fixture. Verify that the report identifies the bad line and exits with code `2` rather than silently treating corrupted input as healthy.

```sh
printf '{not-json}\n' >> "$LAB_ROOT/var/log/checkout/access.jsonl"
set +e
python3 01-linux-and-scripting/host-incident-lab/scripts/analyze_access_log.py \
  "$LAB_ROOT/var/log/checkout/access.jsonl" --max-5xx-rate 5 \
  > "$LAB_ROOT/malformed-report.json"
ANALYZER_EXIT=$?
set -e
test "$ANALYZER_EXIT" -eq 2
cat "$LAB_ROOT/malformed-report.json"
```

## 5. Run regression tests and preserve evidence

Run the standard-library tests, then verify the repository fixture is unchanged:

```sh
python3 -m unittest discover \
  -s 01-linux-and-scripting/host-incident-lab/scripts \
  -p 'test_*.py' -v
sha256sum 01-linux-and-scripting/host-incident-lab/fixtures/access.jsonl
```

Write an incident note containing: scope and time window, report metrics, observed host-resource checks, hypotheses and missing evidence, immediate mitigations that are safe to consider, owner/next update time, and verification/rollback criteria. Do not rotate or delete logs until retention, open-file behavior, and recovery requirements are understood.

## Acceptance Criteria

- The exercise touches only the copied temporary workspace and all original fixture checksums remain unchanged.
- The analyzer has deterministic exit behavior and unit tests cover the normal, malformed, and invalid-field paths.
- The report distinguishes 4xx from 5xx and documents the p95 method.
- The report compares the baseline and degraded release/minute windows without asserting causality from correlation alone.
- The synthetic data remains free of real user identifiers/secrets, and high-cardinality IDs are not used as metrics labels.
- The incident note separates observed facts from hypotheses and does not assert an unproven root cause.
- Cleanup verifies the exact temporary-directory prefix before deletion.

## Cleanup

After saving your note outside the temporary workspace, remove only the directory created by step 1:

```sh
case "$LAB_ROOT" in
  "${TMPDIR:-/tmp}"/devops-linux-lab.*) rm -rf -- "$LAB_ROOT" ;;
  *) printf 'Refusing to remove unexpected path: %s\n' "$LAB_ROOT" >&2; exit 1 ;;
esac
unset LAB_ROOT
```

## Answer Key

See [worked analysis and example incident note](answer.md) after completing the tasks.
