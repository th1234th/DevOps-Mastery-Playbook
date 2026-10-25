# Private GitHub Actions Runner Image Lab

## Outcome and safety model

Build and publish three private runner image variants, deploy an ephemeral GitHub Actions Runner Controller (ARC) scale set to Kubernetes, route a least-privilege smoke workflow to it, and verify a runner is removed after one job.

This lab uses GitHub.com, a private repository, GHCR, and a Kubernetes cluster you control. Self-hosted runners execute repository code with the runner host's network reachability. Do not use these runners for public repositories, untrusted fork pull requests, or production secrets. Keep the runner namespace and its network access separate from production workloads.

The image family is:

| Image target/tag | Tools | Intended jobs |
| --- | --- | --- |
| `base` | ARC runner, curl, git, jq, Python 3 | Lightweight checks and scripts |
| `node` | Base plus Node.js and npm | Node build/test jobs |
| `build` | Base plus compiler toolchain, Go, Python venv | Local source compilation and tests |

The `build` image does not expose the host Docker socket and does not run a privileged Docker-in-Docker daemon. To build OCI images, use a separately secured remote BuildKit service or a deliberately reviewed build service. Do not mount `/var/run/docker.sock` into the runner: that grants the job control over the host/container runtime.

## Prerequisites

- A private GitHub repository in an organization you administer.
- GitHub Actions enabled for that repository.
- A Kubernetes cluster for ARC, Helm 3, kubectl, Docker/Buildx, and permission to create the ARC CRDs and controller RBAC.
- A GitHub App installed on the target organization/repository with the minimum runner-management permission needed by ARC. Use GitHub App authentication rather than a long-lived PAT. Keep the app private key in an approved secret manager.
- A private GHCR package containing the custom image, plus a read-only pull credential for the Kubernetes namespace or an equivalent workload identity integration.

ARC does not need to run on the same cluster as production. A dedicated runner cluster or strongly isolated node pool is preferable.

## 1. Build and publish the image family

The included workflow `.github/workflows/validate-runner-images.yml` builds and smoke-tests all three targets on pull requests without registry credentials or publishing permissions. After review and merge, `.github/workflows/publish-private-runner-images.yml` uses GitHub-hosted runners for the image bootstrap, logs in to GHCR with the job-scoped `GITHUB_TOKEN`, and publishes each target with the commit SHA in its tag. It requests SBOM and provenance attestations. Review/pin third-party workflow actions according to your supply-chain policy before enabling publishing.

Enable the `packages: write` job permission, then dispatch **Publish private runner image family** or push a change to the Dockerfile on `main`. Check each matrix job and confirm these package tags were produced:

```text
ghcr.io/<lowercase-owner>/private-actions-runner:base-<commit-sha>
ghcr.io/<lowercase-owner>/private-actions-runner:node-<commit-sha>
ghcr.io/<lowercase-owner>/private-actions-runner:build-<commit-sha>
```

Set the GHCR package visibility to **Private** and grant only the intended organization/repository read access. Record the image digest for deployment. Do not use `latest` for a runner image in a controlled environment. The ARC base runner image is versioned in the Dockerfile; update it through a reviewed PR and rebuild all variants promptly when runner security releases require it.

Optional local build checks:

```sh
docker build --target base -t private-actions-runner:base 03-gitops-and-strategy/github-runner-lab/runner-image
docker build --target node -t private-actions-runner:node 03-gitops-and-strategy/github-runner-lab/runner-image
docker build --target build -t private-actions-runner:build 03-gitops-and-strategy/github-runner-lab/runner-image
docker run --rm --entrypoint /bin/sh private-actions-runner:build -c 'id; git --version; jq --version; python3 --version; go version; test -x /home/runner/run.sh'
```

## 2. Create isolated Kubernetes namespaces and credentials

Install the ARC controller in `arc-systems` and create the runner scale set in a separate `arc-runners` namespace, as recommended by GitHub. The version used when this lab was validated is `0.15.1`; review the release notes and pin the controller and scale-set charts to the same version:

```sh
ARC_CHART_VERSION=0.15.1
helm upgrade --install arc-controller \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller \
  --namespace arc-systems --create-namespace \
  --version "$ARC_CHART_VERSION" --wait --timeout 10m
kubectl create namespace arc-runners
```

Create an `arc-github-app` Secret in `arc-runners` with keys `github_app_id`, `github_app_installation_id`, and `github_app_private_key`. Populate it via your secret manager/External Secrets integration; do not commit a Secret manifest, put the private key in Helm values, or type it into a command that will be saved in shell history. The Secret must be in the same namespace as the runner scale set.

Create a `ghcr-pull` image-pull Secret in `arc-runners` using a narrowly scoped read-only package credential, or configure the cluster's approved registry credential provider. Do not reuse a write-capable publish credential. The pull Secret is mounted at the PodSpec level; it is never copied into the runner image.

## 3. Deploy the scale set with the private image

Copy `arc/runner-set-values.yaml` to a secure local working file. Replace the GitHub config URL and image owner/tag with your private repository and the exact `build-<commit-sha>` image tag or digest. Keep `githubConfigSecret: arc-github-app`; it references the Secret rather than embedding credentials.

Install the runner scale set using the same pinned ARC chart version:

```sh
helm upgrade --install private-build \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set \
  --namespace arc-runners \
  --version "$ARC_CHART_VERSION" \
  --values /secure/path/runner-set-values.yaml \
  --set controllerServiceAccount.namespace=arc-systems \
  --set controllerServiceAccount.name=arc-controller-gha-rs-controller \
  --wait --timeout 10m
kubectl -n arc-systems get pods
kubectl -n arc-runners get pods
helm -n arc-runners list
```

Do not configure `containerMode: dind` for this image. Docker-in-Docker requires privileged execution in common configurations; this lab intentionally avoids that privilege. ARC creates ephemeral runners and scales down to zero when idle. `private-build` is the scale-set name used by workflow `runs-on`.

## 4. Run the smoke workflow

The included `.github/workflows/private-runner-smoke.yml` uses `workflow_dispatch`, `permissions: contents: read`, and `runs-on: private-build`. Restrict the workflow to trusted maintainers/branches; do not add `pull_request_target`, fork PR checkout, or untrusted repository execution to the runner.

Dispatch **Private ARC runner smoke test** from the private repository. Verify the job succeeds and the image's toolchain appears in the logs. Then inspect lifecycle:

```sh
kubectl -n arc-runners get pods --watch
kubectl -n arc-runners get events --sort-by=.lastTimestamp
```

After the job completes, ARC should remove the ephemeral runner Pod and scale the idle runner count to zero. The scale-set listener/controller can remain running.

## 5. Break/fix exercise

In the secure values file, change the runner image tag to a nonexistent private tag, then upgrade the scale set. Tasks:

1. Diagnose `ImagePullBackOff` from runner Pod events; distinguish registry authorization from a missing tag.
2. Confirm the workflow remains queued because no matching runner is online.
3. Restore the exact known-good tag/digest, run `helm upgrade` again, and verify the smoke workflow completes.
4. Record the failed image reference, event evidence, time to restore capacity, and how the image tag was recovered.

Do not make the registry package public as a troubleshooting shortcut. Do not print Secret data while diagnosing pulls.

## Acceptance and operations

- The three image variants are published to a private package with traceable commit tags and attestations.
- The runner image contains `/home/runner/run.sh` and runs under the `runner` account; it contains no registration token, GitHub App key, registry password, cloud credential, or personal data.
- ARC authenticates with a GitHub App Secret; the runner Pod gets only read-only image-pull credentials.
- Runner Pods are ephemeral, capped at two concurrent runners, created in the isolated namespace, and targeted only by trusted workflow jobs.
- A smoke job starts and the runner Pod disappears after the job.
- The broken-image drill is diagnosed from Pod events and recovered by restoring the desired image reference.
- Preserve ARC controller/listener and runner logs in external log storage before production deployment; ephemeral Pod logs disappear with the Pod.

Review runner-group repository allowlists, outbound network policy, node identity/metadata access, resource quotas, image scanning/signing, action pinning, and runner software update cadence before production use. A custom image is not a security boundary: any job running on it can execute arbitrary code with its effective permissions and network reach.

## Cleanup

First remove the scale set, then remove the controller only if no other scale sets use it:

```sh
helm uninstall private-build --namespace arc-runners
helm uninstall arc-controller --namespace arc-systems
kubectl delete namespace arc-runners arc-systems
```

Delete the private runner package version after its retention/rollback period. Keep the lab's registry credential and GitHub App key out of Git; revoke or rotate them if they were exposed.

## References

- [Actions Runner Controller](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller)
- [Deploying runner scale sets](https://docs.github.com/en/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets)
- [Self-hosted runner security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Runner autoscaling and ephemeral runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners#autoscaling)
- [Custom runner image requirements](https://docs.github.com/en/actions/concepts/runners/actions-runner-controller#creating-your-own-runner-image)
