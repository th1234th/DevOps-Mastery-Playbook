# 10. Cluster Maintenance Lab: Drain and Upgrade Planning

## Goal and safety boundary

Practice a controlled worker-node maintenance cycle with `cordon`, `drain`, a PodDisruptionBudget, workload verification, and `uncordon`. Then produce a version-specific kubeadm upgrade plan. The executable portion uses a disposable Kind cluster; the kubeadm extension requires disposable Ubuntu VMs and is not executable against Kind or a shared cluster.

Never run drain, package upgrades, kubeadm, or reboot commands against a cluster you do not own. Confirm context before each operation. Kind does not emulate host package or kubelet upgrades.

## Track A: Safe Drain and Return

Prerequisites: Docker, Kind, kubectl. From repository root:

```sh
kind create cluster --config 02-containerization/kubernetes/labs/maintenance/kind-config.yaml
kubectl config use-context kind-maintenance-lab
kubectl wait --for=condition=Ready nodes --all --timeout=180s
kubectl apply -f 02-containerization/kubernetes/labs/maintenance/workload.yaml
kubectl -n maintenance-lab rollout status deployment/web --timeout=120s
kubectl -n maintenance-lab get pods -o wide
kubectl -n maintenance-lab get pdb
```

The Deployment has two replicas with preferred anti-affinity, so the scheduler normally spreads them across workers but can place both on one worker if needed. Its PDB requires at least one available replica during voluntary eviction.

Tasks:

1. Choose a worker hosting one `web` Pod. Record node readiness, Pod placement, and PDB allowance.
2. Cordon and drain that worker using the commands below. Observe where the evicted Pod is recreated and why it cannot return to the cordoned node.
3. Verify one available Pod remained during eviction; verify the replacement becomes Ready on the other worker.
4. Uncordon the node and prove it is schedulable again. Preferred anti-affinity can keep the replacement on the other worker, so do not expect it to move back automatically.

Worked commands (replace `<worker-node>` with a worker hosting one web Pod):

```sh
kubectl cordon <worker-node>
kubectl drain <worker-node> --ignore-daemonsets --timeout=120s
kubectl get nodes
kubectl -n maintenance-lab get pods -o wide
kubectl -n maintenance-lab get pdb
kubectl uncordon <worker-node>
kubectl get nodes
kubectl -n maintenance-lab rollout status deployment/web --timeout=120s
```

Do not add `--force` or data-deletion flags to make a blocked drain pass. Inspect the PDB and workload ownership first. DaemonSet Pods are not evicted by the default drain operation; this lab has no application DaemonSet.

## Track B: kubeadm Upgrade Rehearsal Plan

Prerequisites: a disposable, multi-VM Ubuntu cluster installed with kubeadm, an etcd/application backup, console access, and a target Kubernetes minor release supported by that cluster's distribution. This guide deliberately does not hard-code a minor version or package repository because support and package pinning change over time. Select one exact patch release, then follow that release's official [kubeadm upgrade guide](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/) and [version-skew policy](https://kubernetes.io/releases/version-skew-policy/).

Tasks:

1. Record current control-plane, kubelet, kubectl, runtime, and target versions. Check release notes, skew limits, API removals, and add-on compatibility.
2. Take and verify etcd and application-data backups using the distribution procedure. Record the restore path and recovery owner.
3. Upgrade one control-plane node using the version-specific kubeadm guide. Verify API readiness before proceeding.
4. Upgrade workers one at a time: cordon, drain, update kubelet (and kubectl if used on that node), restart kubelet, verify Node Ready and workload health, then uncordon.
5. Record any blocked eviction, error, rollback decision, and post-upgrade smoke test.

Command shape to adapt only after following the target release guide:

```sh
kubectl get nodes -o wide
kubeadm version
kubeadm upgrade plan
sudo kubeadm upgrade apply <target-version>
kubectl cordon <worker-node>
kubectl drain <worker-node> --ignore-daemonsets --timeout=10m
sudo kubeadm upgrade node
sudo systemctl restart kubelet
kubectl get node <worker-node>
kubectl uncordon <worker-node>
```

Package-manager steps, `kubeadm upgrade node` sequencing, and exact flags depend on OS, repository, and Kubernetes version. Use the official procedure for those steps; do not paste these placeholders as a complete upgrade script.

## Verification and Cleanup

Track A passes when the node returns `Ready` and `SchedulingDisabled` is gone, both Deployment replicas are Ready, the Service has endpoints, and the PDB is healthy. Track B passes only when every component version is supported, nodes are Ready, workloads pass smoke checks, and backup/restore evidence is recorded.

Delete only the disposable Kind cluster:

```sh
kind delete cluster --name maintenance-lab
```

For VM cleanup, use the hypervisor or cloud sandbox's documented deletion workflow after recording results. Do not run destructive cleanup against a non-lab cluster.
