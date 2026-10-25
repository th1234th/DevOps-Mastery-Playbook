# 03. Liveness, Readiness, and Startup Probes

Kubernetes does not infer application health from a running process. Configure probes around distinct questions:

- **Startup:** Has a slow-starting application completed initialization? While this probe is failing, liveness and readiness checks are held back.
- **Liveness:** Is this process irrecoverably stuck such that restarting it may help?
- **Readiness:** Should this instance receive new traffic right now?

The [probe demo manifest](manifests/probes-demo.yaml) uses HTTP endpoints on a sample container. Replace the image and paths with endpoints implemented by your application before using it.

## Design rules

- Do not make liveness depend on a remote database or shared service. A dependency outage can otherwise trigger synchronized restarts and amplify the incident.
- Readiness may include dependencies when serving without them is unsafe; consider timeouts and whether the dependency is truly required for every request.
- Keep health endpoints cheap and bounded. They should not expose sensitive details.
- Tune `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `failureThreshold`, and `successThreshold` from measured startup and recovery behavior.
- A probe only checks the configured signal; it is not end-to-end monitoring or an SLO.

## Exercise

In a local cluster, make the test endpoint fail readiness while keeping liveness healthy, then simulate an unrecoverable local hang and observe restart count. Capture events and explain why each state transition occurred. Avoid intentionally injecting failures into shared environments.