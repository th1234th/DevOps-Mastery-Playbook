# GitOps and Delivery Strategy

## Branching and promotion

Keep the default branch releasable. Prefer short-lived branches, small pull requests, automated checks, and explicit review ownership. Promote the same immutable artifact through environments; do not rebuild a different image for production. Use environment-specific configuration with visible review and auditable approvals.

There is no universal branching model. Choose trunk-based development or release branches based on release cadence and support constraints, then document how urgent fixes are propagated and how long-lived divergence is prevented.

See [branching strategy](git-branching-strategy.md) and [multi-cluster troubleshooting](multi-cluster-gitops-troubleshooting.md).

## Delivery quality gates

- Unit and integration tests appropriate to the changed behavior.
- Static analysis, dependency and image scanning, and infrastructure policy checks.
- A clear policy for severity thresholds, exceptions, owners, and expiration; a raw coverage percentage is not a proxy for test quality.
- A deployment health check, rollout timeout, and tested rollback or forward-fix strategy.
- Protected production environments and approval rules that match the service's risk.

Example scanners to evaluate include [Trivy](https://trivy.dev/) and [Checkov](https://www.checkov.io/). Pin tools and actions according to your organization's supply-chain policy and review their permissions before adoption.