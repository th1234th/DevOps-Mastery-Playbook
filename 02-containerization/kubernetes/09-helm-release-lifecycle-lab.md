# 09. Helm Release Lifecycle Lab

## Goal and safety boundary

Render and inspect a local chart, install it as a release, upgrade its values, inspect history, roll back, verify the workload, and uninstall it. The chart uses the public `nginx:1.27-alpine` image and does not install a third-party chart or require chart repositories.

## Setup

Prerequisites: Docker, Kind, kubectl, Helm 3. Run from the repository root:

```sh
helm version
kind create cluster --name helm-lab
kubectl config use-context kind-helm-lab
kubectl wait --for=condition=Ready nodes --all --timeout=180s
```

Chart path: `02-containerization/kubernetes/labs/helm/release-lab`.

## Tasks

1. Lint and render the chart without installing it. Identify the rendered Deployment, Service selector, image, replicas, and resource requests.
2. Install release `web` in namespace `helm-lab`; verify it reaches one ready replica.
3. Upgrade to two replicas and image tag `1.27`; inspect release history and confirm the live Deployment changed.
4. Roll back to the first revision. Verify the replica count and image return to the initial values.
5. Uninstall the release and confirm its workload resources are gone.

## Worked Answer

```sh
helm lint 02-containerization/kubernetes/labs/helm/release-lab
helm template web 02-containerization/kubernetes/labs/helm/release-lab --namespace helm-lab
helm install web 02-containerization/kubernetes/labs/helm/release-lab --namespace helm-lab --create-namespace --wait --timeout 120s
helm status web --namespace helm-lab
kubectl -n helm-lab get deployment,pod,service
```

For the upgrade and rollback:

```sh
helm upgrade web 02-containerization/kubernetes/labs/helm/release-lab --namespace helm-lab --set replicaCount=2 --set image.tag=1.27 --wait --timeout 120s
helm history web --namespace helm-lab
kubectl -n helm-lab get deployment web -o jsonpath='{.spec.replicas}{" "}{.spec.template.spec.containers[0].image}{"\n"}'
helm rollback web 1 --namespace helm-lab --wait --timeout 120s
helm history web --namespace helm-lab
kubectl -n helm-lab get deployment web -o jsonpath='{.spec.replicas}{" "}{.spec.template.spec.containers[0].image}{"\n"}'
kubectl -n helm-lab rollout status deployment/web --timeout=120s
```

The initial revision is one replica of `nginx:1.27-alpine`; revision 2 is two replicas of `nginx:1.27`; rollback creates a new history revision with the initial configuration. Confirm exact tags in the rendered chart and cluster output rather than relying only on revision numbers.

## Verification and Cleanup

Before rollback: Deployment `2/2` ready and image `nginx:1.27`. After rollback: Deployment `1/1` ready and image `nginx:1.27-alpine`. After uninstall:

```sh
helm uninstall web --namespace helm-lab
kubectl -n helm-lab get deployment,service
```

The final `kubectl get` should report no matching resources. Delete only the test cluster:

```sh
kind delete cluster --name helm-lab
```

## Further Practice

Add a staging values file, then compare `helm template` output between values sets. Do not place credentials in values files committed to Git; Helm release data is not a substitute for a secret manager. Review rendered manifests before installing any chart outside this exercise.
