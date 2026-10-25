# Argo CD Monitoring: End-to-End Lab

## Outcome

Deploy Argo CD and a small Prometheus/Grafana stack into a disposable Kind cluster, scrape Argo CD's application-controller, API-server, and repo-server metrics, alert on an unhealthy or out-of-sync Application, diagnose a bad Git revision, and recover by reverting desired state.

This is a single-cluster learning deployment, not a production HA design. The monitoring chart and Argo CD download container images and chart dependencies. Use a disposable cluster with at least 4 CPUs and 8 GiB free memory. Never use a production kubeconfig.

## Prerequisites

- Docker, Kind, kubectl, Helm 3, Git, curl.
- A Git repository reachable by the Argo CD repo-server. Push this repository or a practice fork so the `demo-app` path exists on the selected branch. For a private repository, configure a read-only deploy key or approved repository credential through the Argo CD secret mechanism; do not put credentials in the Application YAML.
- A working directory without uncommitted changes for the failure/revert exercise, or use a dedicated practice clone.

## 1. Create the isolated cluster

```sh
kind create cluster --name argocd-monitoring --config 03-gitops-and-strategy/argocd-monitoring-lab/kind-config.yaml
kubectl config use-context kind-argocd-monitoring
kubectl config current-context
kubectl wait --for=condition=Ready nodes --all --timeout=180s
```

If you already have a Kind cluster named `argocd-monitoring`, stop and choose a different name/config rather than deleting an unknown cluster.

## 2. Install Prometheus and Grafana

Review `monitoring/values.yaml`, including its reduced retention and resource requests. Select a current reviewed chart version and pin it for repeatable runs:

```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm search repo prometheus-community/kube-prometheus-stack --versions | head
```

The version used when this lab was validated is `92.13.1`. Set the variable explicitly so the run is reproducible; review the chart changelog before selecting a newer release.

```sh
STACK_CHART_VERSION=92.13.1
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --version "$STACK_CHART_VERSION" \
  --values 03-gitops-and-strategy/argocd-monitoring-lab/monitoring/values.yaml \
  --wait --timeout 10m
kubectl -n monitoring get pods
```

## 3. Install Argo CD

The version used when this lab was validated is `v3.5.6`. Review its release notes and set the tag explicitly before applying:

```sh
ARGOCD_VERSION=v3.5.6
kubectl create namespace argocd
kubectl apply --server-side --force-conflicts -n argocd -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"
kubectl -n argocd rollout status deployment/argocd-server --timeout=10m
kubectl -n argocd get pods,services
```

The standard install is cluster-admin capable because this lab deploys an Application back into the same cluster. This is acceptable only for the disposable lab. For production, choose a least-privilege installation model and separate target clusters/permissions as documented by Argo CD. The server-side apply command follows the selected release's published install instructions.

## 4. Configure Prometheus scraping and alerts

Apply the ServiceMonitors and PrometheusRule. They select Argo CD's standard metrics Services and use the Prometheus Operator label `release: monitoring` to match the Helm release name. If your pinned Argo CD/chart versions label the Services differently, inspect them and adjust the selectors rather than creating duplicate Services.

```sh
kubectl apply -f 03-gitops-and-strategy/argocd-monitoring-lab/monitoring/servicemonitors.yaml
kubectl apply -f 03-gitops-and-strategy/argocd-monitoring-lab/monitoring/prometheusrule.yaml
kubectl apply -f 03-gitops-and-strategy/argocd-monitoring-lab/monitoring/grafana-dashboard.yaml
kubectl -n argocd get services --show-labels
kubectl -n argocd get servicemonitors
kubectl -n monitoring get prometheusrules
kubectl -n monitoring get configmap argocd-operations-dashboard
```

Prometheus Operator reconciliation is asynchronous. Allow at least two scrape intervals, then refresh `/targets`; do not treat an immediately empty target list after `kubectl apply` as a failed configuration. The target scrape pools should be named `serviceMonitor/argocd/argocd-application-controller/0`, `serviceMonitor/argocd/argocd-server/0`, and `serviceMonitor/argocd/argocd-repo-server/0`, and each should become `UP`.

Forward Prometheus and Grafana in separate terminals:

```sh
kubectl -n monitoring port-forward service/monitoring-kube-prometheus-prometheus 9090:9090
kubectl -n monitoring port-forward service/monitoring-grafana 3000:80
kubectl -n monitoring port-forward service/monitoring-kube-prometheus-alertmanager 9093:9093
```

Open Prometheus at `http://127.0.0.1:9090/targets` and confirm all three Argo CD jobs are `UP`. In Prometheus Graph, query `argocd_app_info`, `argocd_app_reconcile`, and `argocd_git_request_total`. Application metrics may have no application series until an Argo CD Application is registered and reconciled; the repo-server metric may not have a sample until a Git request occurs. An empty result before those events is not a scrape failure. Open Grafana at `http://127.0.0.1:3000`; obtain the lab admin password from the chart-generated Secret without printing it into a shared log. The chart provisions Prometheus as a Grafana data source, and its dashboard sidecar should import the `Argo CD Operations` dashboard from the applied ConfigMap. Confirm its panels show application health/sync counts and Git request rate once the Application has reconciled.

Open Alertmanager at `http://127.0.0.1:9093` and verify Prometheus rules arrive there when they fire. The lab values enable Alertmanager but deliberately do not configure an external receiver. For real notifications, configure an approved receiver and secret reference, route by severity/team, and test delivery without placing tokens or passwords in Git. A firing Prometheus rule alone is not proof that an operator was notified.

The application-controller metrics are exposed by `argocd-metrics:8082`, server metrics by `argocd-server-metrics:8083`, and repo-server metrics by `argocd-repo-server:8084` in the standard install. Check the pinned version's metrics documentation; names and endpoints can change.

## 5. Connect a Git-managed demo Application

Set `REPO_URL` to the HTTPS/SSH clone URL for your pushed copy of this repository and `APP_REVISION` to the branch containing the lab files. Create the Application from the provided template after replacing those two placeholder values:

```sh
cp 03-gitops-and-strategy/argocd-monitoring-lab/argocd/application.yaml /tmp/argocd-demo-application.yaml
```

Edit `/tmp/argocd-demo-application.yaml` to set `.spec.source.repoURL` and `.spec.source.targetRevision`, then apply it:

```sh
kubectl apply -f /tmp/argocd-demo-application.yaml
kubectl -n argocd get applications
kubectl -n demo-app get deployment,service,pods
```

The Application deploys the manifests in `demo-app/`. Confirm the Application becomes `Synced` and `Healthy`, and query `argocd_app_info` in Prometheus.

## 6. Trigger, detect, and recover from a GitOps incident

In a practice clone, change the demo Deployment image to a nonexistent tag, commit, and push that change to the branch Argo CD watches. Do not make this change in a shared/protected branch.

Tasks:

1. Observe the Application sync/health state in the Argo CD UI and `kubectl -n argocd get application demo-app -o yaml`.
2. Query `argocd_app_info` and confirm the `sync_status`/`health_status` labels change. Inspect Prometheus Alerts and identify whether the provided rule is Pending or Firing.
3. Trace the symptom to the new ReplicaSet/Pod and image-pull events. Explain why the Git commit remains `Synced` even though workload health is degraded.
4. Revert the faulty commit and push. Wait for Argo CD reconciliation, then verify `Synced` + `Healthy`, ready Pods, and cleared alert.

Useful evidence commands:

```sh
kubectl -n argocd get application demo-app -o wide
kubectl -n demo-app get deployment,pods,events --sort-by=.lastTimestamp
kubectl -n monitoring get prometheusrule
```

Do not repair the live Deployment with `kubectl edit`; Git is the source of truth and Argo CD will reconcile manual drift.

### Expected diagnosis

| Observation | Likely layer | Evidence and next check |
| --- | --- | --- |
| A ServiceMonitor target is absent | Discovery/selector configuration | Confirm the ServiceMonitor's `release: monitoring` label, Prometheus `serviceMonitorSelector`, namespace selection, Argo CD Service labels, and named `metrics` port. |
| Target exists but is `DOWN` | Endpoint/network/metrics endpoint | Inspect the Service endpoints and port, then query the corresponding `/metrics` endpoint from inside the cluster. Check NetworkPolicy and scrape errors before changing labels. |
| Application is `OutOfSync` | Git revision/rendering/reconciliation | Inspect `.status.sync`, repo-server logs/events, target revision, path, and rendered manifests. Distinguish a Git fetch/manifest-generation error from a valid diff awaiting sync. |
| Application is `Synced` but `Degraded` | Workload runtime/health | The desired commit applied, but resources are unhealthy. Inspect ReplicaSets, Pods, image reference, events, and Argo health details. A successful sync is not proof that traffic is healthy. |
| Prometheus rule is pending, then firing | Alert evaluation | The rule's `for` period must elapse with samples present. Verify the `argocd_app_info` labels and Prometheus rule page; a missing metric is not equivalent to a healthy application. |
| Prometheus alert fires but no notification arrives | Alertmanager route/receiver | Check that the alert reaches Alertmanager, then inspect route matching, receiver health, delivery errors, and secret references. This lab intentionally has no external receiver configured. |

For the intentionally bad image revision, Argo CD should normally remain `Synced` because the live spec matches Git while health becomes `Degraded` due to image-pull failure. The `ArgoCDApplicationNotHealthy` alert should transition from inactive to pending and then firing after two minutes. Reverting the Git commit should restore Pod readiness, application health, and eventually clear the alert. If the application is instead `OutOfSync`, investigate reconciliation or manual drift before attributing it to the bad image.

## Acceptance and operator evidence

Record pinned chart and Argo CD versions, target Git revision, metrics targets and query results, initial/failed/recovered Application states, the image-pull evidence, alert timing, recovery revision, and any resource constraints. The lab passes when:

- Prometheus scrapes controller, API-server, and repo-server metrics successfully.
- Grafana imports the provisioned Argo CD dashboard and its panels return data.
- Alertmanager receives firing rules; external notification delivery is configured and tested separately if required.
- The Git-managed Application reaches `Synced` and `Healthy` at baseline.
- The deliberately invalid image produces an observable health degradation and Prometheus alert.
- Reverting Git restores the workload, Application health, and alert state without direct cluster edits.
- Staging is isolated from the lab; no credentials are committed or printed.

## Cleanup

Stop the port-forward processes, then remove only the named disposable cluster:

```sh
kind delete cluster --name argocd-monitoring
```

## References

- [Argo CD metrics](https://argo-cd.readthedocs.io/en/stable/operator-manual/metrics/)
- [Argo CD installation](https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/)
- [Prometheus Community Helm charts](https://prometheus-community.github.io/helm-charts/)
