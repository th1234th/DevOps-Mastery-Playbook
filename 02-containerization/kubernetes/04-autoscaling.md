# 04. Autoscaling: HPA, VPA, and Cluster Autoscaler

| Mechanism | Scales | Typical signal | Key limitation |
| --- | --- | --- | --- |
| HPA | Replica count of a workload | CPU/memory utilization or custom/external metrics | Needs usable metrics and correctly declared resource requests for utilization-based scaling. |
| VPA | Pod resource requests/limits recommendations or values | Historical and current resource use | In-place support and restart behavior depend on Kubernetes/VPA versions and configuration; avoid conflicting ownership with HPA on the same metric. |
| Cluster Autoscaler | Node count in a node group | Pods that cannot schedule and underutilized nodes | Provider integration, quotas, provisioning delay, and Pod constraints bound the result. |

The [HPA demo](manifests/hpa-demo.yaml) is a sample policy, not a full load test. It requires the Metrics API (commonly Metrics Server) and a target Deployment with resource requests.

## Capacity chain

1. Increased demand raises utilization or a custom metric.
2. HPA requests more replicas, subject to its bounds and stabilization behavior.
3. The scheduler places Pods if suitable capacity exists.
4. Unschedulable Pods may prompt cluster autoscaling, if node pools, quotas, and constraints allow it.
5. New nodes take time to provision and become ready; scaling is not instantaneous.

## Exercise

In a disposable cluster, generate controlled load against your own sample service. Observe metrics, replica changes, scheduling events, and node capacity. Define a maximum replica count, load-test budget, and cleanup step. Explain the effect of missing requests, unavailable metrics, PodDisruptionBudgets, topology constraints, and cloud quota exhaustion.