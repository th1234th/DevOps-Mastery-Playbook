# End-to-End Release Lab

## Scenario

You own a small HTTP service called `release-lab`. Build one container image, deploy that same image to staging and production in a local Kubernetes cluster, and demonstrate that a bad production readiness check is detected and recovered through Git. Finish with evidence another operator could use during an incident.

This lab uses a disposable [Kind](https://kind.sigs.k8s.io/) cluster. It needs Docker, `kind`, `kubectl`, Git, Python 3, and `curl`. No cloud account, registry credentials, or production cluster is needed. Run commands from the repository root. Do not point these commands at a cluster you care about.

## 1. Prepare and inspect

Confirm your current Kubernetes context and start a named local cluster:

```sh
kubectl config current-context
kind create cluster --name release-lab
kubectl config use-context kind-release-lab
kubectl get nodes
```

Read `app/server.py`, the `Dockerfile`, and the base and overlay manifests before applying anything. Record the expected service endpoints and which manifest owns each environment's replica count.

## 2. Build one artifact

Build and inspect the image, then make that same local image available to Kind:

```sh
docker build -t release-lab:1.0.0 03-gitops-and-strategy/end-to-end-release-lab/app
docker image inspect release-lab:1.0.0 --format '{{.Id}} {{.Config.User}}'
kind load docker-image release-lab:1.0.0 --name release-lab
```

Record the image ID and confirm the configured container user is non-root. Do not rebuild between environments.

## 3. Deploy and verify staging

Render the overlay first, then apply it:

```sh
kubectl kustomize 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/staging
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/staging
kubectl -n release-lab-staging rollout status deployment/release-lab --timeout=90s
kubectl -n release-lab-staging get deployment,pods,service
```

In a second terminal, forward the service port and query the application. Stop port-forward with Ctrl-C when done.

```sh
kubectl -n release-lab-staging port-forward service/release-lab 8080:80
```

```sh
curl -fsS http://127.0.0.1:8080/
curl -fsS http://127.0.0.1:8080/readyz
```

Confirm the deployment is ready and the response reports version `1.0.0`.

## 4. Promote the same image to production

Before applying production, compare the rendered image reference with staging. Apply the production overlay and verify its replica count and health:

```sh
kubectl kustomize 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-production rollout status deployment/release-lab --timeout=90s
kubectl -n release-lab-production get deployment,pods,service
```

Both overlays must use `release-lab:1.0.0` in separate namespaces; confirm staging remains 1/1 ready while production is 2/2 ready.

## 5. Simulate and diagnose a failed release

Use a clean working tree or a practice clone. Create a short-lived branch, change only `k8s/overlays/production/readiness.yaml` from `/readyz` to `/ready`, inspect the diff, and commit the simulated change:

```sh
git switch -c exercise/readiness-failure
git diff --check
git diff -- 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
git add 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
git commit -m "Simulate production readiness regression"
```

Apply the changed desired state and collect evidence. The rollout-status command is expected to time out/fail in this step; that is the exercise, not a reason to skip the diagnosis.

```sh
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-production rollout status deployment/release-lab --timeout=30s
kubectl -n release-lab-production get deployment,pods
kubectl -n release-lab-production describe deployment/release-lab
kubectl -n release-lab-production get events --sort-by=.lastTimestamp
kubectl -n release-lab-production get endpointslice -l kubernetes.io/service-name=release-lab
```

Explain why the process can be live while the new Pod is excluded from ready Service endpoints. Check whether old replicas continue serving during the stalled rolling update. Identify the exact desired-state change before recovering.

## 6. Recover through Git and verify

Revert the simulated commit, apply the reverted desired state, and verify the recovery:

```sh
git revert --no-edit HEAD
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-production rollout status deployment/release-lab --timeout=90s
kubectl -n release-lab-production get deployment,pods,endpointslice
```

Repeat the port-forward and HTTP checks against `release-lab-production`. Confirm production has two ready replicas and Service endpoints again, and staging remains healthy. Do not fix the cluster with an imperative `kubectl edit`; the Git revision is the source of truth.

## 7. Diagnose a Service selector failure

This second failure drill practices labels, selectors, Services, EndpointSlices, and evidence-led network troubleshooting. On the same branch, change only the production Service selector in `k8s/overlays/production/service-selector.yaml` from `release-lab` to `release-lab-missing`, inspect and commit it, then apply the production overlay:

```sh
git diff --check
git diff -- 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production/service-selector.yaml
git add 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production/service-selector.yaml
git commit -m "Simulate production Service selector regression"
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-production get service,pods,endpointslice --show-labels
kubectl -n release-lab-production describe service/release-lab
```

The Pods should stay ready, but the Service should have no matching endpoints. Explain why this is a Service selection problem, not a failed Deployment or container. Revert the faulty commit and reconcile:

```sh
git revert --no-edit HEAD
kubectl apply -k 03-gitops-and-strategy/end-to-end-release-lab/k8s/overlays/production
kubectl -n release-lab-production get service,endpointslice
kubectl -n release-lab-production rollout status deployment/release-lab --timeout=90s
```

Verify staging is unaffected throughout by checking its Deployment and EndpointSlice in `release-lab-staging`.

## 8. Leave operator evidence

Write a short release/incident note containing:

- Image tag and image ID promoted to both environments.
- Staging and production rollout results.
- The failed probe path, the evidence that isolated it, and customer-visible impact (or the test that would detect it).
- The mismatched Service selector, its endpoint evidence, and proof staging remained isolated.
- Recovery revision and the post-recovery checks.
- One preventive review or automated test that would catch this exact regression.

## Acceptance criteria

- The application image runs as a non-root user and responds on `/`, `/livez`, and `/readyz`.
- Staging and production use the same image; both become healthy before the fault is introduced.
- Staging and production run concurrently in different namespaces; a production-only failure does not change staging.
- The bad production probe leaves new pods unready and excludes them from ready Service endpoints while existing healthy replicas continue serving.
- The bad Service selector leaves Pods healthy but produces no Service endpoints; reverting it restores endpoints.
- Recovery is committed to Git, reconciled with `kubectl apply -k`, and verified by rollout and HTTP checks.
- The evidence note explains symptoms, diagnosis, recovery, and prevention.

## Cleanup

When all evidence is recorded, delete only the named lab cluster:

```sh
kind delete cluster --name release-lab
```

The [answer key](answer.md) shows one complete implementation and expected observations. Try the exercise before reading it.