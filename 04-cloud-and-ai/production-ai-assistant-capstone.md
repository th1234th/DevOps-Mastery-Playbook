# Production AI Assistant: Architecture and Operations Capstone

## Scenario

Design and rehearse the release of an internal support assistant that retrieves approved policy documents and drafts answers for a human support agent. It must not make decisions or send customer responses without review.

This is an executable design-and-tabletop exercise, not a cloud deployment. It requires no provider account, model API key, customer data, or spend. Use the fictional data below and the worksheet; verify each decision against your chosen provider's current security, privacy, availability, and pricing documentation before any real implementation.

## Fictional requirements

- 2,000 support agents; 120,000 assistant requests/month, with a 5x business-hour peak.
- Availability objective: 99.9% monthly for the application path. Planned maintenance is included in the measurement unless explicitly excluded by the service agreement.
- Interactive latency objective: p95 <= 2.0 seconds, measured from the application edge through retrieval and model response. Streamed first-token latency must also be recorded separately.
- Quality objective: at least 90% of a reviewed, approved evaluation set has a supported answer or an explicit abstention; no unsupported citation is acceptable in the critical policy subset.
- Budget ceiling: $2,000/month for model, retrieval, storage, and observability. Cloud infrastructure is tracked separately with a tagged budget.
- Data boundary: internal policy documents are approved for the chosen service. Prompts may contain customer identifiers. Raw prompts and responses must not enter general application logs or third-party traces by default.
- Human review is mandatory. On provider/model outage, retrieval outage, low confidence, or safety check failure, show a clear unavailable/abstain state and preserve the existing support workflow.

## Tasks

Work in a copy of this worksheet. State assumptions; unsupported facts should be marked `unknown` and assigned an owner.

1. **Draw the path:** user/UI, identity, application API, authorization, retrieval/index, model endpoint, safety/evaluation checks, audit record, and human approval. Mark trust boundaries and data flows.
2. **Choose controls:** workload identity, secret handling, network egress, encryption, data retention, tenant isolation, audit access, and provider data-processing constraints.
3. **Define release controls:** model identifier/version, prompt/template version, retrieval corpus/index version, feature flag, evaluation gate, staged rollout, kill switch, and rollback/forward-fix conditions.
4. **Define operations:** availability and latency indicators, quality/safety measurements, cost/usage limits, dashboards, actionable alerts, owner, and degradation behavior.
5. **Run the failure tabletop:** choose one of the injects below. Write the first five diagnostics, safe mitigation, communication, recovery test, and evidence to preserve.
6. **Calculate the availability budget:** use a 30-day month and state the allowed unavailable time for 99.9%. Explain which user-facing events count as unavailable.
7. **Make a cost plan:** provide a formula and budget guardrail. Do not invent provider prices; identify the pricing facts to retrieve and the owner for them.
8. **Complete the acceptance checklist** and produce a one-page ADR plus a runbook stub. No live infrastructure is provisioned.

## Failure Injects

Choose one and ask a peer to reveal it after baseline design:

| Inject | Signals supplied when asked | Constraint |
| --- | --- | --- |
| Model provider latency/outage | Provider p95 rises to 8 seconds; timeout rate is 18%; retrieval remains healthy | Do not silently retry without a bounded retry budget or promise a completion time. |
| Retrieval corpus regression | Index version changed; citation coverage fell from 94% to 61%; model endpoint is healthy | Do not solve a retrieval-quality problem by increasing model temperature or removing citations. |
| Spend anomaly | Token use is 3x forecast after an agent workflow change; monthly forecast is $2,700 | Preserve safe support functionality; apply a bounded spend control and investigate the workload source. |
| Sensitive prompt in trace | A trace contains a customer email and account number | Treat as a potential data exposure; stop further capture, restrict access, preserve audit evidence, and follow the organization's incident process. |

## Design Worksheet

```text
Owner / review date:
Workload and business outcome:
Data classification and allowed provider processing:
Trust boundaries and identities:
Model / prompt / corpus version tuple:
Availability SLI and SLO:
Latency SLI and SLO (edge, first-token, complete response):
Quality/safety evaluation gate:
Cost formula, budget, and hard controls:
Failure inject and user impact:
Detection / alert / owner:
Mitigation and graceful degradation:
Rollback or forward-fix criteria:
Recovery verification:
Unknowns and owners:
```

## Acceptance Criteria

- Every data flow has an identity, classification, retention, and access-control decision.
- No real prompt, response, customer record, or credential is placed in Git or general metrics labels.
- The human approval boundary remains in place in all failure modes.
- Model, prompt, and retrieval corpus are independently versioned and can be rolled back.
- SLOs, quality gates, and cost limits have measurable indicators, thresholds, and owners.
- Degradation is explicit and safe; recovery includes a user-facing verification, not just a green provider status.
- Cloud-specific unknowns (regional availability, pricing, data processing, limits) are assigned for verification, not guessed.

Read the [worked answer](production-ai-assistant-capstone-answer.md) after completing your design.
