# Production Incident Tabletop: Worked Response

## Initial Command

**Severity:** Declare the service's user-impact severity according to its incident policy; given elevated write failures on a ledger API, begin at the high-impact response tier until scope proves otherwise. Do not equate a dashboard color with severity.

**Roles:** Name one IC, operations lead, communications lead, and scribe. The IC coordinates and avoids making every technical change. Establish a dedicated incident channel and a 10-minute user/status update cadence. Record UTC timestamps.

**Initial facts:** A release reached 25% of traffic at 09:00; alerts began 09:08; 5xx and write timeouts are elevated. The causal relationship is a hypothesis, not yet proven. Safe first checks: compare canary/control cohorts, inspect user-facing golden signals, and correlate deploy/configuration events with application/dependency telemetry. Pause further rollout while gathering evidence.

## Example Timeline

| Time UTC | Observation / decision | Owner | Verification |
| --- | --- | --- | --- |
| 09:08 | Alert acknowledged; incident channel opened; rollout paused at 25%. Impact scope and affected operations confirmed. | IC / operations | Canary and control cohort dashboard, synthetic write check |
| 09:12 | Canary 5xx 28%, control 1%; p95 4.2s vs. 350ms baseline; pool acquisition timeouts observed. Relationship to release is strong but still being tested. | Scribe / service owner | Logs and traces correlated by request IDs in approved tooling |
| 09:14 | IC authorizes rollback to the recorded prior digest; operations lead executes; a second operator verifies the intended revision. | Operations | Deployment status, canary error rate, synthetic write |
| 09:20 | 5xx falls to 2%, but connection saturation remains elevated; rollback alone is incomplete recovery. No second speculative config change is made yet. | IC / service owner | Pool metrics, queue depth, error and latency trends |
| 09:23 | Compare prior/current pool settings and database capacity. Approve one bounded, reversible pool correction only if the current fleet-wide connection budget remains below database capacity. | Service owner / operations | Aggregate connection count, pool wait, DB health, canary behavior |
| 09:30 | User-facing errors near baseline for five minutes; keep elevated monitoring and do not yet declare resolved. | IC | Synthetic writes, 5xx, p95, dependency saturation |
| 09:40 | Recovery declared after agreed stability window, queue drain, successful writes, and no renewed saturation. | IC | User-path checks and service SLO indicators |

The exact mitigation can differ. The key is one owned change at a time, a known rollback target, a connection-capacity calculation before increasing pools, and user-path verification after each change.

## Example User Status

“We are investigating elevated failures on ledger writes beginning around 09:08 UTC. Some requests are delayed or fail; reads are currently less affected. We paused the rollout and are testing a recovery. Next update by 09:20 UTC, or sooner if impact changes.”

At recovery: “Ledger writes have returned near normal and have remained stable through our verification window. We are continuing to monitor connection saturation and will share a follow-up after the review.” Do not expose internal stack traces or identify individual engineers.

## Review of the Sample Change

**Blocking comment:** “Please provide load-test evidence and the maximum total connection budget across all replicas before raising each pool from 40 to 120; this could exceed database capacity and worsen saturation.”

**Question:** “What failures are retried, and how does this retry policy interact with client retries, request deadlines, and the shared database retry budget?”

**Approval conditions:** Specify bounded retries with jitter and an end-to-end deadline, demonstrate load/chaos results, add pool-wait/saturation alerts, confirm staged rollout and rollback to the prior digest/config, and document an owner/runbook. The change is not approved based only on increasing limits.

## Blameless Review

**Impact:** Some users experienced delayed or failed ledger writes. Quantify duration and affected request share from approved telemetry before publishing final figures.

**Contributing conditions:** A pool-size increase was rolled out without an aggregate fleet/database capacity check; retries amplified demand; the canary detected the issue but the rollout pause depended on human response. These describe system conditions, not an individual's intent or competence.

**What helped:** Cohort comparison, deployment event correlation, a known prior immutable digest, a paused rollout, and a clear incident lead.

**Follow-up actions:**

1. Add a CI policy/test that computes maximum aggregate pool connections against the database budget. Owner: platform team; due date set in the review.
2. Define a shared retry budget and deadline propagation; add a test for simultaneous client/service retries. Owner: service team.
3. Automate canary rollback when the agreed error/latency burn threshold is exceeded, with a documented manual override. Owner: release engineering.
4. Add a dashboard panel and actionable alert for pool wait, active connections, and rejected connections. Owner: database operations.
5. Run a blameless game day to verify rollback and user communications. Owner: service owner.

Each action should have one accountable owner, a due date, and a verifiable completion condition. Avoid “be more careful” or “add more monitoring” without specifying the control and evidence.
