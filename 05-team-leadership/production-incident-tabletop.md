# Production Incident and Change Review Tabletop

## Purpose and safety

Practice incident command, customer-focused mitigation, evidence handling, blameless learning, and risk-based code review. This is a 45-60 minute tabletop using fictional information only; do not touch production systems or disclose customer data. One person can facilitate and play all roles, though a group exercise is more realistic.

## Service context

The fictional `ledger-api` has a 99.9% monthly availability SLO, measured on valid user requests. A release was deployed to 25% of traffic at 09:00 UTC. At 09:08, the error budget dashboard shows elevated 5xx responses and checkout/ledger writes are timing out. The current deployment system supports traffic rollback to the prior immutable image digest.

Roles: incident commander (IC), operations lead, communications lead, service owner, and scribe. For a solo exercise, write which role you are playing at each decision.

## Exercise Tasks

1. **First five minutes:** State severity, user impact, incident roles, update cadence, and the first three safe diagnostic checks. Separate observations from assumptions.
2. **Inject A at minute 8:** Error rate is 28% for the canary cohort and 1% for the rest. p95 latency is 4.2 seconds (baseline 350 ms). Logs show database pool acquisition timeouts. Choose whether to pause rollout, rollback, mitigate, or gather more evidence; state who executes and who verifies.
3. **Inject B at minute 18:** Rollback reduces errors to 2% but does not restore baseline. A dependency dashboard shows database connection saturation; a connection pool configuration changed in the same release. Decide the next reversible action and how to avoid competing changes.
4. **Inject C at minute 30:** User-facing errors are back near baseline for five minutes. A manager asks for an immediate root cause and names the engineer who merged the change. Respond without speculating or blaming.
5. Write an external status update, a private handoff, recovery criteria, and a blameless review with at least three owned follow-up actions.
6. Review the sample change below using [code review standards](code-review-standards.md). Write one blocking comment, one question, and one approval condition.

### Sample change for review

```diff
- pool_max_connections = 40
+ pool_max_connections = 120
+ retry_count = 5
+ retry_delay_ms = 100
```

No load test, rollout plan, retry budget, rollback note, or alert change is included in the PR description.

## Deliverables

- A timeline with timestamps, facts, decisions, owners, and verification.
- A status update suitable for affected users, with impact and next update time.
- A safe recovery plan and measurable recovery criteria.
- A blameless review: contributing conditions, detection, response, and systemic actions.
- A review decision and specific required evidence for the sample change.

Use the [worked facilitator response](production-incident-tabletop-answer.md) after the exercise. Different actions can be valid when they are evidence-based, reversible, and clearly owned.
