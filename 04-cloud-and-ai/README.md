# Cloud and AI Operations Labs

Use an isolated account or project, budget alerts, least-privileged roles, and cleanup automation. Cloud resources can incur charges even when a lab appears idle. Never commit credentials or personal data.

## Cloud foundations

1. **Identity:** Create a narrowly scoped workload identity; demonstrate access denial outside its role. Prefer short-lived federation over long-lived keys.
2. **Network:** Diagram trust boundaries, ingress/egress paths, DNS, and private service access. Test intended paths and document denied paths.
3. **Infrastructure as code:** Provision a small non-production service from reviewed code, run a plan/policy check, and destroy it. Keep state encrypted and access-controlled.
4. **Reliability:** Define a failure scenario, recovery objectives, backup coverage, and restore validation. Test in a non-production environment.
5. **Cost:** Set a budget, tag ownership and expiry, and compare estimated with observed cost before cleanup.

## AWS and Google Cloud

Map equivalent concepts rather than memorizing service names: identity federation and workload roles, managed Kubernetes, private networking, artifact registries, secret stores, audit logs, and budget controls. Use the providers' official documentation and free-tier terms; verify current prices and regional limits before provisioning.

## AI service operations

For a model-backed service, treat the model and its dependencies as production supply-chain components:

- Define data classification, consent, retention, and redaction rules before sending prompts or documents to an external service.
- Store model identifiers and endpoint configuration as versioned deployment inputs; do not assume model behavior remains constant across provider updates.
- Evaluate quality and safety on representative, approved datasets; track regressions, latency, availability, and cost.
- Keep human review and fallback behavior for high-impact decisions. Define how users report incorrect or unsafe outputs.
- Protect API keys with a secret manager, use least privilege, set budgets and rate limits, and log metadata without unnecessarily retaining sensitive prompt content.
- Document provider dependency, regional availability, data processing terms, and a graceful degradation plan.

## Deliverable

Create a one-page architecture decision record that includes assumptions, threat boundaries, failure modes, monitoring, cost controls, and cleanup/rollback steps.

For a complete fictional scenario with SLO calculations, versioned model/prompt/retrieval releases, privacy boundaries, evaluation gates, cost controls, failure injects, and a worked response, complete the [production AI assistant capstone](production-ai-assistant-capstone.md) and review its [worked answer](production-ai-assistant-capstone-answer.md). It is a design/tabletop exercise and intentionally provisions no cloud resources or external model calls.
