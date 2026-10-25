# 05. Air-Gapped Kubernetes Deployment

An air-gapped deployment is a supply-chain and operations design problem, not just a matter of downloading a few images. Define the boundary (fully disconnected, restricted egress, or controlled transfer) and the update process first.

## Release inventory

- Kubernetes distribution packages, OS packages, kernel modules, and required binaries for the exact supported versions and architectures.
- Container images referenced by all manifests, charts, operators, and transitive workloads, including init containers and admission components.
- Helm charts and dependencies, plugins, CRDs, and required schemas.
- CA bundles, signing keys, policy bundles, and configuration with a documented trust and rotation process.
- SBOMs, signatures, provenance attestations, vulnerability reports, and checksums transferred through the approved channel.

## Delivery procedure

1. Build and test in a connected staging environment; pin artifacts by immutable digest.
2. Generate an inventory and verify signatures/checksums before transfer.
3. Import artifacts into the approved internal registry and mirror all referenced names without changing digests unexpectedly.
4. Scan and policy-check the imported artifacts; record exceptions and expiry dates.
5. Deploy from the internal source, validate image pulls and cluster health, and retain a tested rollback bundle.
6. Rehearse the next update and revocation path, including what happens when a signing key or critical artifact is compromised.

## Lead-level checks

Can the platform be rebuilt from only the approved offline bundle? Are DNS, time synchronization, certificate issuance, identity, logging, and metrics also available inside the boundary? Who owns the recurring transfer, patch cadence, and evidence trail?