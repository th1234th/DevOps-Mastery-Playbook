# Multi-Cluster GitOps Troubleshooting

## Scenario

An application is healthy in staging but fails to sync or become healthy in production. Diagnose from evidence before changing desired state.

## Triage sequence

1. **Scope:** Identify the affected application, cluster, namespace, revision, and first failing timestamp. Confirm whether the issue is sync, health, or runtime behavior.
2. **Compare inputs:** Check commit SHA, rendered manifests, chart and image digests, substitutions, and environment overlays. Ensure production did not receive a different artifact.
3. **Check destination:** Verify the configured API endpoint, cluster registration, namespace, network reachability, and supported API versions.
4. **Check authorization:** Inspect the GitOps controller's service-account permissions and admission-policy denials. Grant only the missing permission after review.
5. **Check ordering and dependencies:** Review sync waves, health checks, CRDs/operators, hooks, and whether dependencies are actually ready.
6. **Check external inputs:** Verify secret delivery through the approved secret manager, without printing secret values. Check image-pull access, DNS, certificates, quotas, and cloud dependencies.
7. **Check drift and reconciliation:** Inspect controller status, events, audit logs, and recent manual changes. Avoid making a direct production edit that the controller will revert or that bypasses review.
8. **Recover:** Use the documented rollback or forward-fix path. Record the evidence and update alerts or runbooks if the failure was not diagnosable.

## Common causes

- API-version differences or missing CRDs between clusters.
- Incorrect destination credentials or insufficient RBAC.
- Different rendered values, image references, or unavailable registry artifacts.
- Secret synchronization delay or mismatched secret references.
- Out-of-order resources, unhealthy dependencies, or admission policies.
- Controller/repository webhook delay, stale cache, or network access failure.
- Direct manual mutation causing drift.

Treat “App of Apps” as an organizational pattern, not a fix for unclear ownership or dependency ordering. Keep application boundaries, sync ownership, and rollback scope explicit.