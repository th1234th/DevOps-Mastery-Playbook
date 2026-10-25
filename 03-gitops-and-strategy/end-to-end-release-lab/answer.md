# End-to-End Release Lab: Answer Key

This is one valid solution, not the only acceptable wording for the evidence note. Run it only against the disposable `kind-release-lab` cluster created by the [exercise](README.md).

## Application and container

`app/server.py` uses Python's standard library, so there are no runtime packages to download. It returns a JSON version response at `/`, `200 OK` at `/livez` and `/readyz`, and `404` for unknown paths. The Dockerfile sets a fixed version, copies the application as UID/GID 65534, and starts Python as that non-root user.

Inspect the built image with:

```sh
docker image inspect release-lab:1.0.0 --format '{{.Id}} {{.Config.User}}'
```

The user should be `65534:65534`. Save the returned image ID; the image reference in each environment is the same local tag, and the image is built only once.

## Desired state

The base Kustomize package defines a two-replica Deployment and a ClusterIP Service. The container exposes port 8080; the Service maps port 80 to 8080. Startup and liveness checks use the app's health endpoint. The production overlay explicitly sets its readiness check at `/readyz`, and the staging Deployment inherits the same path from the base. CPU and memory requests/limits are set, and the image uses `IfNotPresent` so Kind can use the image loaded locally.

The staging overlay sets one replica in `release-lab-staging`; production sets two in `release-lab-production`. Both include the same base resources and image `release-lab:1.0.0`, but run concurrently in separate namespaces. Each overlay includes its Namespace object so `kubectl apply -k` bootstraps the environment.

Useful checks before and after promotion:

```sh
kubectl kustomize 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/staging
kubectl kustomize 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-staging rollout status deployment/release-lab --timeout=90s
kubectl -n release-lab-staging get deployment,pods,endpointslice
kubectl -n release-lab-production rollout status deployment/release-lab --timeout=90s
kubectl -n release-lab-production get deployment,pods,endpointslice
```

The rendered image field should be identical in both overlays. Staging should show one ready replica and production two. Applying production must not scale or replace the staging Deployment.

## Fault diagnosis

The simulated bad commit changes `k8s/overlays/production/readiness.yaml` from `/readyz` to `/ready`. The app has no such route, so kubelet's HTTP readiness check receives `404`. The containers can still answer `/livez`, so they need not restart. The new Pods remain unready and are excluded from ready Service endpoints. With the default rolling-update strategy, the old healthy replicas stay available while the rollout is stalled; this drill should not cause an outage. The key evidence is the probe path in the Deployment description plus the new Pod's readiness/events and EndpointSlice endpoint conditions.

This is a desired-state/configuration regression, not a broken image, scheduling failure, or liveness failure. Rebuilding the image or deleting pods would not fix the incorrect probe.

Expected checks while the fault is present:

```sh
kubectl -n release-lab-production get deployment
kubectl -n release-lab-production describe deployment/release-lab
kubectl -n release-lab-production get pods
kubectl -n release-lab-production get endpointslice -l kubernetes.io/service-name=release-lab
```

The rollout should be stalled with one updated replica, two old ready replicas, and an unready replacement Pod. Pod events/conditions report readiness probe failures. The EndpointSlice can list all three Pod addresses; inspect its `conditions.ready` values to distinguish the two serving old replicas from the unready replacement.

## Recovery

The exercise's recovery is a Git revert of the isolated bad commit:

```sh
git revert --no-edit HEAD
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-production rollout status deployment/release-lab --timeout=90s
kubectl -n release-lab-production get deployment,pods,endpointslice
kubectl -n release-lab-staging get deployment,pods,endpointslice
```

The rendered probe is `/readyz` again. The stalled rollout completes with two ready production replicas, while staging remains 1/1. A successful HTTP request through port-forward confirms the app is serving:

```sh
kubectl -n release-lab-production port-forward service/release-lab 8080:80
```

```sh
curl -fsS http://127.0.0.1:8080/
curl -fsS http://127.0.0.1:8080/readyz
```

The root response resembles:

```json
{"service": "release-lab", "version": "1.0.0", "status": "ok"}
```

## Service selector diagnosis

The second simulated commit changes the production Service selector from `app.kubernetes.io/name: release-lab` to `app.kubernetes.io/name: release-lab-missing`. The Deployment and Pods remain healthy because this change does not modify them. The Service now selects no Pods, so its EndpointSlice has no ready addresses and requests through the Service fail.

Inspect both sides of the selector relationship:

```sh
kubectl -n release-lab-production get service/release-lab -o yaml
kubectl -n release-lab-production get pods --show-labels
kubectl -n release-lab-production get endpointslice -l kubernetes.io/service-name=release-lab
```

After `git revert --no-edit HEAD` and reapplying the production overlay, the Service selector matches the Pod label again and ready endpoints return. Staging is unaffected because it has its own Namespace, Service, and Deployment.

## Example evidence note

**Release:** `release-lab:1.0.0`, same local image ID in staging and production. Staging reached 1/1 ready; production reached 2/2 ready before the simulated change.

**Impact:** During the test, the new production pod failed readiness because the overlay configured `/ready`; the app exposes `/readyz`. Liveness remained healthy. The rollout stalled, but the two old healthy replicas remained ready and continued serving, so the default rolling update avoided an outage.

**Diagnosis:** `describe deployment` showed the incorrect readiness path; pod events showed HTTP 404 probe failures; EndpointSlice conditions showed the replacement was unready while old replicas remained ready.

**Networking drill:** The production Service selector was changed to a value no Pod had. Pods stayed ready, but EndpointSlice had no ready addresses. Reverting the selector commit restored Service endpoints. Staging remained healthy in its separate namespace.

**Recovery:** Reverted each isolated configuration commit and reapplied the production overlay. Rollout completed at 2/2 ready, and `/` plus `/readyz` succeeded through port-forward.

**Prevention:** Add a CI check that renders every overlay and verifies probe paths against the application's documented health endpoints; require the rendered production diff and rollout result in review.

## Cleanup

```sh
kind delete cluster --name release-lab
```