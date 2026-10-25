# 07. Storage Lab: PV, PVC, and Pod Replacement

## Goal and safety boundary

Prove that a claim binds to a volume and that data survives replacing a Pod. This lab uses a static `hostPath` volume on a single-node Kind cluster. It is for learning only: node-local `hostPath` storage is not a production persistence or backup design, and deleting the cluster deletes the data.

## Setup

Prerequisites: Docker, Kind, kubectl, and Git. Run from the repository root. Create a disposable cluster and confirm its context:

```sh
kind create cluster --name storage-lab
kubectl config use-context kind-storage-lab
kubectl config current-context
kubectl get nodes -o wide
```

Inspect the manifests in `labs/storage/`. This static PV intentionally uses `storageClassName: storage-lab-manual`, so it does not depend on whether the cluster has a default StorageClass.

## Tasks

1. Apply the namespace, PV, PVC, then writer Deployment. Record the PVC phase and PV claim reference.
2. Read the marker file from the writer and explain which object requests storage and which object represents the supplied volume.
3. Delete only the writer Pod. Wait for its replacement, then confirm the marker file still exists.
4. Explain the limits of this volume and the effect of the `Retain` reclaim policy.

## Worked Answer

```sh
kubectl apply -f 02-containerization/kubernetes/labs/storage/namespace.yaml
kubectl -n storage-lab wait --for=create serviceaccount/default --timeout=60s
kubectl apply -f 02-containerization/kubernetes/labs/storage/persistent-volume.yaml
kubectl apply -f 02-containerization/kubernetes/labs/storage/persistent-volume-claim.yaml
kubectl apply -f 02-containerization/kubernetes/labs/storage/writer-pod.yaml
kubectl -n storage-lab rollout status deployment/writer --timeout=120s
kubectl get pv storage-lab-pv
kubectl -n storage-lab get pvc checkpoint -o wide
kubectl -n storage-lab exec deployment/writer -- cat /data/checkpoints.log
kubectl -n storage-lab delete pod -l app=writer
kubectl -n storage-lab rollout status deployment/writer --timeout=120s
kubectl -n storage-lab exec deployment/writer -- cat /data/checkpoints.log
```

Expected: the PVC is `Bound` to `storage-lab-pv`; the writer appends UTC timestamps; the timestamps remain after the Pod is recreated because the PVC still mounts the same node directory. The PVC is the namespaced request; the PV is the cluster-scoped capacity/backing-volume object. `Retain` preserves the PV's data after claim release and requires deliberate manual reclamation. It does not protect data if the node or Kind cluster is deleted.

## Verification and Cleanup

The proof is: PVC `Bound`, Deployment `Available`, marker present before and after controller-managed Pod replacement. Clean up only this lab cluster:

```sh
kind delete cluster --name storage-lab
```

If cleaning resources without deleting the cluster, delete the Pod, then the PVC, inspect the PV (which remains `Released` because reclaim policy is `Retain`), and only then delete the lab PV. Never use these cleanup commands against a shared cluster.

## Further Practice

Use a cluster-provided CSI StorageClass to request a dynamically provisioned claim. Compare `ReadWriteOnce`, `ReadOnlyMany`, and `ReadWriteMany` support against the actual driver; an access mode is not a backup or a guarantee that every storage backend supports concurrent writers.
