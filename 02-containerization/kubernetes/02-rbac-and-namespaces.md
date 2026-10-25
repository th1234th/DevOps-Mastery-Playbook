# 02. RBAC and Namespace Isolation

## Scenario

A developer should be able to list and inspect Pods in `dev`, but must not change resources or access `production`. The example manifests create a namespace-scoped Role and bind a named user identity to it. Authentication is supplied by the cluster; the YAML does not create credentials.

## Apply and inspect

```sh
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/rbac-readonly.yaml
kubectl auth can-i get pods --as=dev-junior -n dev
kubectl auth can-i delete services --as=dev-junior -n dev
kubectl auth can-i get pods --as=dev-junior -n production
```

Expected authorization answers: `yes`, `no`, `no`. Impersonation checks require the caller to have permission to impersonate that user. A negative `can-i` result is not proof of namespace confidentiality if cluster-wide discovery or other API permissions are granted elsewhere.

## Important boundaries

- A Role is limited to one namespace; a ClusterRole can grant cluster-wide capabilities and needs extra scrutiny.
- A RoleBinding can bind a ClusterRole within one namespace. A ClusterRoleBinding grants access cluster-wide.
- Kubernetes RBAC is additive: there are no deny rules. Check all bindings for the subject, not only the Role shown here.
- Namespace boundaries are not a complete hostile multi-tenant security boundary. Consider separate clusters for strong isolation requirements.
- Add ResourceQuota and LimitRange policies to manage consumption and defaults; they do not replace authorization.

## Exercise

Add narrowly scoped access to read Services, verify that Secret data remains inaccessible, then prove there are no unexpected inherited grants. Record the identity provider, group membership, and audit evidence used for the review.