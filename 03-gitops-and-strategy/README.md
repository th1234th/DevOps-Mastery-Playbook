# GitOps and Delivery Strategy

## Branching and promotion

Keep the default branch releasable. Prefer short-lived branches, small pull requests, automated checks, and explicit review ownership. Promote the same immutable artifact through environments; do not rebuild a different image for production. Use environment-specific configuration with visible review and auditable approvals.

There is no universal branching model. Choose trunk-based development or release branches based on release cadence and support constraints, then document how urgent fixes are propagated and how long-lived divergence is prevented.

See [branching strategy](git-branching-strategy.md) and [multi-cluster troubleshooting](multi-cluster-gitops-troubleshooting.md).

Practice the full path in the [end-to-end release lab](end-to-end-release-lab/README.md); consult its [answer key](end-to-end-release-lab/answer.md) after attempting the tasks.

For controller operations and observability, complete the [Argo CD monitoring lab](argocd-monitoring-lab/README.md). For a private custom runner image and ephemeral Kubernetes-backed GitHub Actions capacity, use the [ARC private runner lab](github-runner-lab/README.md).

The repository's optional [read-only MCP companion](../tools/devops_mcp/README.md) can search the practical catalog and provide the relevant guide as context; it does not operate clusters or alter desired state.

## Delivery quality gates

- Unit and integration tests appropriate to the changed behavior.
- Static analysis, dependency and image scanning, and infrastructure policy checks.
- A clear policy for severity thresholds, exceptions, owners, and expiration; a raw coverage percentage is not a proxy for test quality.
- A deployment health check, rollout timeout, and tested rollback or forward-fix strategy.
- Protected production environments and approval rules that match the service's risk.

Example scanners to evaluate include [Trivy](https://trivy.dev/) and [Checkov](https://www.checkov.io/). Pin tools and actions according to your organization's supply-chain policy and review their permissions before adoption.
