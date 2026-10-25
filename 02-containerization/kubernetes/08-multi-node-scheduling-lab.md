# 08. Multi-Node Scheduling Lab

## Goal and safety boundary

Use node labels, a `nodeSelector`, taints, tolerations, resource requests, and scheduler events to explain where a Pod runs and why another Pod remains Pending. This lab creates three disposable Kind nodes; it does not teach production scheduler or control-plane configuration.

## Setup

Prerequisites: Docker, Kind, kubectl. Run from the repository root:

```sh
kind create cluster --config 02-containerization/kubernetes/labs/scheduling/kind-config.yaml
kubectl config use-context kind-scheduling-lab
kubectl get nodes -o wide
```

Identify the two worker nodes by role, not assumed ordering:

```sh
kubectl get nodes -l '!node-role.kubernetes.io/control-plane' --show-labels
```

Choose one worker as general and the other as reserved. In the commands below, replace `<general-node>` and `<reserved-node>` with names from your output.

## Tasks

1. Label one worker `lab-role=general`; label the other `lab-role=reserved` and taint it `dedicated=reserved:NoSchedule`.
2. Apply `labs/scheduling/workload.yaml`; prove the Pod is scheduled on the general worker.
3. Change the Deployment's selector to `lab-role=reserved`. Observe and explain the Pending Pod.
4. Add a matching toleration. Verify it can now schedule on the reserved worker.
5. Explain the difference: a toleration permits scheduling onto a tainted node; it does not attract the Pod there. The selector supplies the placement requirement.

## Worked Answer

```sh
kubectl label node <general-node> lab-role=general
kubectl label node <reserved-node> lab-role=reserved
kubectl taint node <reserved-node> dedicated=reserved:NoSchedule
kubectl apply -f 02-containerization/kubernetes/labs/scheduling/workload.yaml
kubectl -n scheduling-lab rollout status deployment/placement-demo --timeout=120s
kubectl -n scheduling-lab get pods -o wide
```

The first Pod should run on `<general-node>`. Change the selector and apply the update:

```sh
kubectl -n scheduling-lab patch deployment placement-demo --type=merge -p '{"spec":{"template":{"spec":{"nodeSelector":{"lab-role":"reserved"}}}}}'
kubectl -n scheduling-lab get pods -o wide
kubectl -n scheduling-lab describe pod -l app=placement-demo
kubectl -n scheduling-lab get events --sort-by=.lastTimestamp
```

The replacement cannot use the reserved node because it lacks a toleration for `dedicated=reserved:NoSchedule`; it also cannot use the general worker because its node selector does not match. Add a toleration:

```sh
kubectl -n scheduling-lab patch deployment placement-demo --type=merge -p '{"spec":{"template":{"spec":{"tolerations":[{"key":"dedicated","operator":"Equal","value":"reserved","effect":"NoSchedule"}]}}}}'
kubectl -n scheduling-lab rollout status deployment/placement-demo --timeout=120s
kubectl -n scheduling-lab get pods -o wide
```

The ready Pod should now be on `<reserved-node>`. Its resource request is part of scheduler feasibility; requests are not the same as limits or actual utilization.

## Verification and Cleanup

Verify node labels and taint, Pod `Running`/`Ready`, and `NODE` in `kubectl get pods -o wide`. Events should describe the scheduling constraint before the toleration is added. Delete only this cluster:

```sh
kind delete cluster --name scheduling-lab
```

## Further Practice

Add required node affinity and compare it with a `nodeSelector`. Add a second replica and test preferred pod anti-affinity. Avoid manual `spec.nodeName` in a controller-managed workload unless the task specifically asks for bypassing normal scheduler selection.
