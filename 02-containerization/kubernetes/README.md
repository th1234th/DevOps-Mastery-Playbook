# Kubernetes Operations

These notes assume a disposable test cluster and a supported Kubernetes release. Check the version-specific official docs before using any example in production.

## Core control flow

The API server authenticates and authorizes requests, validates and persists API objects in etcd, and serves the cluster API. The scheduler selects a node for unscheduled Pods. The kubelet on each node observes assigned workloads and asks the container runtime to run them. Controllers continuously compare observed state with desired state and make corrective changes. This reconciliation model is why a successful API request does not guarantee an application is ready to serve.

## Deep dives

- [01. Architecture and etcd](01-architecture-deep-dive.md)
- [02. RBAC and namespace isolation](02-rbac-and-namespaces.md)
- [03. Health probes](03-probes-healthchecks.md)
- [04. Autoscaling](04-autoscaling.md)
- [05. Air-gapped deployment](05-air-gapped-deployment.md)

## Local manifest lab

Review the files in [manifests](manifests/) and apply them only to a lab cluster:

```sh
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/rbac-readonly.yaml
kubectl apply -f manifests/resource-quota.yaml
kubectl apply -f manifests/probes-demo.yaml
kubectl apply -f manifests/hpa-demo.yaml
```

The HPA example includes a sample target Deployment and requires a working metrics API. The manifests are teaching examples, not a complete production baseline. Remove lab resources with `kubectl delete namespace dev` when finished.