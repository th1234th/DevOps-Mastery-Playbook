# 11. Cluster Troubleshooting Lab

## Goal and safety boundary

Practice a repeatable incident method against a disposable Kind cluster: establish a baseline, observe symptoms, isolate the failing layer, change one variable, verify recovery, and record evidence. This lab injects a bad image reference, a Service selector mismatch, and a worker heartbeat loss. It does not reproduce every kubeadm control-plane or production CNI failure.

The node failure stops a Kind worker container. Use it only against the named `troubleshooting-lab` cluster created here, and restart it immediately after collecting the short failure observation. Never stop containers or kubelet on a cluster you do not own.

## Setup

Prerequisites: Docker, Kind, kubectl. From repository root:

```sh
kind create cluster --config 02-containerization/kubernetes/labs/troubleshooting/kind-config.yaml
kubectl config use-context kind-troubleshooting-lab
kubectl wait --for=condition=Ready nodes --all --timeout=180s
kubectl apply -f 02-containerization/kubernetes/labs/troubleshooting/baseline.yaml
kubectl -n troubleshooting-lab rollout status deployment/web --timeout=120s
kubectl -n troubleshooting-lab get deployment,pods,service,endpointslice -o wide
```

## Incident Method

For each fault, record time, namespace, object, expected behavior, observed behavior, evidence, hypothesis, smallest corrective change, and verification. Do not jump directly to deleting Pods; controllers may recreate the same broken specification.

## Scenario A: Image Pull Failure

Task: introduce an invalid image tag, identify whether this is an application crash or image acquisition problem, then restore the baseline declaratively.

Worked answer:

```sh
kubectl -n troubleshooting-lab set image deployment/web web=nginx:does-not-exist
kubectl -n troubleshooting-lab get pods -w
kubectl -n troubleshooting-lab describe pod -l app=web
kubectl -n troubleshooting-lab get events --sort-by=.lastTimestamp
```

Expected: new Pods show `ErrImagePull`/`ImagePullBackOff`; events identify the unavailable tag. Existing healthy replicas may continue serving during the rolling update. Restore the known-good desired state and verify:

```sh
kubectl apply -f 02-containerization/kubernetes/labs/troubleshooting/baseline.yaml
kubectl -n troubleshooting-lab rollout status deployment/web --timeout=120s
kubectl -n troubleshooting-lab get pods
```

## Scenario B: Service Has No Backends

Task: change the Service selector to a label no Pod has. Do not modify the Deployment. Use selectors and EndpointSlices to distinguish this from an application/container failure.

Worked answer:

```sh
kubectl -n troubleshooting-lab patch service web --type=merge -p '{"spec":{"selector":{"app":"missing"}}}'
kubectl -n troubleshooting-lab get pods --show-labels
kubectl -n troubleshooting-lab describe service web
kubectl -n troubleshooting-lab get endpointslice -l kubernetes.io/service-name=web
```

Expected: Pods stay Ready; the EndpointSlice has no backend addresses because the Service selector matches no Pod labels. Restore from the baseline and check endpoints return:

```sh
kubectl apply -f 02-containerization/kubernetes/labs/troubleshooting/baseline.yaml
kubectl -n troubleshooting-lab get endpointslice -l kubernetes.io/service-name=web
kubectl -n troubleshooting-lab rollout status deployment/web --timeout=120s
```

## Scenario C: Worker Stops Renewing Its Lease

Task: pick one Kind worker, simulate loss of its heartbeat from the Docker host, inspect Node conditions/events, restore it, and verify recovery.

Worked answer (the configured node is `troubleshooting-lab-worker`; verify with `kind get nodes --name troubleshooting-lab` first):

```sh
kind get nodes --name troubleshooting-lab
docker stop -t 0 troubleshooting-lab-worker
kubectl get nodes
kubectl describe node troubleshooting-lab-worker
kubectl get events -A --sort-by=.lastTimestamp
```

Watch the Node status for the lease timeout rather than expecting an immediate transition:

```sh
kubectl get nodes --watch
```

Stop the watch with Ctrl-C after the worker changes from `Ready`. Expected: after missed heartbeats, the node eventually shows `NotReady`; its Ready condition is commonly `Unknown` when the kubelet is unreachable (it may differ by Kubernetes version and failure timing). Node conditions/reason and cluster events show the control plane's view. Existing Pods may remain listed on the node while it is unreachable. Do not infer application health merely from stale Pod objects.

Restore the exact node immediately:

```sh
docker start troubleshooting-lab-worker
kubectl wait --for=condition=Ready node/troubleshooting-lab-worker --timeout=180s
kubectl -n troubleshooting-lab rollout status deployment/web --timeout=180s
kubectl -n troubleshooting-lab get pods -o wide
kubectl -n troubleshooting-lab get endpointslice -l kubernetes.io/service-name=web
```

## Verification and Cleanup

The lab passes when each fault has a distinct evidence trail and is corrected at its owning layer: image reference, Service selector, or node heartbeat. After all scenarios, both replicas should be Ready and Service endpoints should exist. Remove the disposable cluster:

```sh
kind delete cluster --name troubleshooting-lab
```

## Limits and Extension

For kubelet, container-runtime, API-server, scheduler, or etcd logs, use a disposable kubeadm VM cluster with host access and a tested recovery path. Kind node logs can be inspected with `docker exec <kind-node> journalctl ...` only if the node image exposes the relevant service manager; containerd logs and control-plane components vary by Kind/Kubernetes version. Do not stop or edit control-plane components as a first troubleshooting exercise.
