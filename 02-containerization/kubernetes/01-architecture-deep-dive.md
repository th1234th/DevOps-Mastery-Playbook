# 01. Kubernetes Architecture and etcd

## Learn the request path

Trace a Deployment update from a client request through API authentication, authorization, admission, persistence, reconciliation, scheduling, kubelet action, and application readiness. At each step, identify the component that owns the decision and the evidence it emits.

## etcd responsibilities

etcd is the Kubernetes control plane's consistent key-value store. It is not an application database. Protect its availability, access, encryption, and backups as control-plane critical infrastructure. In managed Kubernetes, the provider usually operates the control-plane data store; do not attempt to operate or restore it directly.

## Lab checklist

In a local cluster where you control the control plane:

1. Read the distribution's supported backup procedure and record the exact version and datastore topology.
2. Take an authenticated snapshot using the documented tool and protect the snapshot as sensitive data.
3. Verify snapshot metadata and practice restoration into a disposable isolated control plane. Never restore over a shared or production cluster as an exercise.
4. Record restore duration, validation checks, and recovery gaps. A backup without a tested restore is an assumption, not a recovery plan.
5. Review datastore health and latency using the distribution's supported metrics. Understand compaction and defragmentation before attempting maintenance; schedule and monitor it because it can affect availability.

## Lead-level questions

- What is the tested recovery point and recovery time objective?
- Who can access snapshots, and how are they encrypted, retained, and deleted?
- Which failure modes are handled by the control-plane provider versus your team?
- How do you distinguish datastore latency from API server, network, or admission latency?

Use the [official cluster administration documentation](https://kubernetes.io/docs/tasks/administer-cluster/) and your distribution's runbook. Do not copy etcd commands from an unrelated topology.