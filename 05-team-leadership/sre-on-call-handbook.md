# SRE and On-Call Handbook

## Service readiness

Every owned service should have a named team, service description, dependency map, dashboards, alert routes, SLOs, deployment and rollback procedure, and a current runbook. An alert should prompt a clear action; use tickets or dashboards for non-urgent diagnostic information.

## Golden signals

- **Latency:** Request duration, including tail percentiles and endpoint differences.
- **Traffic:** Request rate or relevant workload volume.
- **Errors:** Failed or incorrect outcomes, not only HTTP 5xx responses.
- **Saturation:** Resource or queue pressure that predicts inability to serve demand.

## Incident response

1. Acknowledge the page and establish an incident lead when impact warrants it.
2. Assess user impact and scope; communicate status at a predictable cadence.
3. Stabilize first using reversible, understood actions. Avoid speculative concurrent changes.
4. Preserve a timeline and evidence while protecting customer data and credentials.
5. Confirm recovery with user-facing signals, not only green infrastructure dashboards.
6. Hold a blameless review focused on contributing conditions, detection, response, and systemic improvements.

## On-call health

Define primary and secondary coverage, escalation paths, handoff notes, and an owner for every alert. Track alert volume and after-hours burden. Repeated manual actions are candidates for automation; repeated pages with no action are candidates for redesign or removal. Do not normalize chronic overload as an individual performance issue.

## Runbook minimum

Each runbook states symptoms, user impact, safe diagnostics, mitigations, rollback criteria, escalation contacts, and verification of recovery. Link the runbook from the alert and keep it usable by someone outside the service's authoring team.