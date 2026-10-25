# Production AI Assistant Capstone: Worked Answer

This is an example architecture and response, not provider-specific infrastructure code. Validate actual service names, pricing, regional behavior, data-processing terms, quotas, and security controls for the provider you select.

## Example Architecture Decision

**Decision:** Keep the support workflow authoritative. The assistant retrieves from a versioned, approved policy corpus and returns a draft with citations and a confidence/abstention state. An authenticated support agent reviews and submits the final response. The model has no direct write access to customer records or ticket actions.

**Request path:** Agent UI -> SSO -> application API -> authorization and tenant/context check -> retrieval service -> approved vector/search index -> model endpoint -> output/citation validation -> draft shown to agent -> human approval -> existing ticket system. Audit events record actor, timestamp, model/prompt/index version, decision state, and safe correlation ID; raw prompt and output content are excluded from general telemetry. A separately controlled, short-retention review process may access approved samples for evaluation.

**Trust boundary:** The model provider is an external processor unless contract and deployment facts establish otherwise. Send the minimum necessary content, redact direct identifiers where possible, use approved endpoints/regions, and verify retention/training behavior in the current provider agreement. Encrypt data in transit and at rest. Use workload identity and short-lived credentials; no long-lived API key in an image, source tree, or command argument.

**Network and identity:** Application workload identity can call only the approved retrieval/model endpoints and read only its own secret references. The model has no cloud control-plane permissions. Restrict egress to required endpoints where operationally feasible. Separate admin, operator, evaluator, and service identities; log privileged access.

## SLO and Evaluation

For a 30-day month, 99.9% availability permits 0.1% unavailable time:

$$30 \times 24 \times 60 \times 0.001 = 43.2\text{ minutes}$$

Count a request as available only if the user receives a safe result within the agreed deadline: a grounded draft, an explicit abstention, or the documented graceful fallback. A fast but unsupported answer is not success. Publish separate indicators for edge request success, full-response p95, first-token p95, retrieval availability, abstention rate, citation support, and human correction/override. Define denominators, exclusions, minimum sample sizes, and evaluation windows before alerting.

Evaluation gate example: run a fixed, access-controlled dataset with approved expected citations before any model, prompt, retrieval, or safety-policy change. Require >=90% supported-answer-or-correct-abstention overall and 100% supported citation behavior on the critical policy subset. Also test prompt injection, conflicting documents, stale policy, PII, and refusal cases. A human quality owner approves promotion; aggregate automated scores alone do not authorize customer-facing automation.

## Release and Recovery

Record an immutable tuple: model provider/model/version, prompt template commit, safety-policy version, retrieval corpus/index version, application image digest, and evaluation dataset/version. Promote through test -> internal pilot -> limited production cohort -> general availability. Use a feature flag and explicit kill switch. Keep the prior tuple available.

Rollback when critical citation support regresses, privacy controls fail, the quality gate fails, user-facing SLO burn exceeds the agreed threshold, or cost controls cannot contain the workload. Roll back the smallest implicated component where compatible; preserve compatibility between prompt/index/model contracts. Verify with synthetic requests and a reviewed evaluation slice, then confirm safe behavior in the user workflow.

## Cost Guardrail

Do not invent a dollar estimate. Measure the variables and retrieve current provider rates:

```text
monthly_model_cost = requests * (input_tokens_per_request * input_rate
                               + output_tokens_per_request * output_rate)
monthly_retrieval_cost = query_count * retrieval_rate
                         + indexed_storage_gb * storage_rate
monthly_total = model + retrieval + application + storage + observability
```

Track actual and forecast cost by service/team/environment using bounded labels. Alert at 70% and 85% of the $2,000 model/retrieval budget; at 95%, disable nonessential batch evaluation and reduce optional context/token caps. Do not disable safety checks or human review as a cost response. Enforce per-user rate limits, maximum context/output tokens, request deadlines, and a kill switch. Confirm billing delay, quotas, and hard-spend-control capabilities with the provider.

## Example Failure Response: Sensitive Prompt in Trace

1. Declare a suspected data-handling incident and identify the affected service, trace backend, time range, and access scope.
2. Stop further prompt/response capture in general tracing through the approved configuration or feature flag. Keep the service in a safe mode if redaction cannot be proven.
3. Restrict trace access and retention through the incident procedure; preserve audit metadata and evidence without copying the sensitive prompt into chat or this report.
4. Identify who accessed the data and whether the provider or downstream exporter retained copies. Escalate to privacy/security owners based on policy; do not make unsupported breach claims.
5. Test redaction with synthetic canary values, inspect traces and logs, verify ordinary application telemetry still works, and get the data owner/security sign-off before re-enabling capture.
6. Record timeline, scope, contributing controls, notification decision owner, and corrective actions. Validate that high-cardinality IDs and raw content are absent from metrics.

## Example ADR Summary

**Status:** Proposed for limited internal pilot. **Risk:** Provider dependency, retrieval quality drift, privacy exposure, and unbounded token spend. **Controls:** SSO/workload identity, minimum data disclosure, no raw content in general logs/traces, versioned corpus/prompt/model, deterministic evaluation gate, human approval, explicit abstention/fallback, request/token limits, cost budget, and rollback tuple. **Open questions:** selected provider's current data-processing terms, regional failover, per-token prices, quotas, and deletion guarantees. Assign named owners before implementation.
