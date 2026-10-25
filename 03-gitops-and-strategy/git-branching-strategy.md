# Git Branching Strategy

## Default recommendation

For teams that release continuously, use trunk-based development: short-lived branches, frequent integration, feature flags for incomplete user-facing work, and release artifacts tagged by immutable digest. Protect the main branch with required checks and review appropriate to risk.

## Define these team decisions

- What is the source of truth for desired state and application configuration?
- How are urgent fixes released, and how are they merged back to ongoing work?
- Which changes require a second reviewer or security/platform approval?
- How are migrations made backward-compatible across rolling deployments?
- How do teams promote and roll back the same artifact across dev, staging, and production?
- What is the policy for stale branches, generated files, and release tags?

## Exercise

Simulate a defective release in a throwaway repository. Compare revert, redeploying the previous immutable artifact, and a forward fix. Include database compatibility, feature flags, auditability, and incident communication in the decision. Do not rewrite shared branch history to hide a production change.