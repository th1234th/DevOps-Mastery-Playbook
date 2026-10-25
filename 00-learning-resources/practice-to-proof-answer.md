# Practice-to-Proof Lab: Example Answer

This sample demonstrates the level of evidence expected. Use your own resource, versions, output, and conclusions.

```text
Topic and resource: Container image hardening; official Docker build documentation
Outcome: Build and verify a non-root HTTP image with a read-only root filesystem in 90 minutes.
Environment and version: Disposable local Docker Engine; image tag image-lab:1.0.0
Safety boundary: Local loopback only; no registry push, host socket mount, credentials, or production data.
Baseline prediction: The image should expose only the app's HTTP port and run as a numeric non-root UID.
Reproduction command/task: Run the production image lab's tests, build command, and constrained docker run commands.
Expected result: Three unit tests pass; /healthz returns 200; root endpoint reports the configured version; unknown path returns 404.
Actual result: Record the learner's own output. Example: all three tests passed and an early curl failed before the health probe completed.
Failure diagnosed: The process was still starting; Docker health changed from starting to healthy. No image code change was needed.
Verification evidence: docker inspect reported user 10001:10001 and read_only=true; health was healthy; HTTP smoke checks passed.
Cleanup confirmation: Stopped the exact named image-lab container and verified it no longer existed.
Five-minute explanation: A running container is not automatically ready; wait for its health signal, then verify service behavior independently.
One-week recall result: Leave blank until repeating without notes.
Next objective: Compare the local tag with a digest-pinned deployment and explain the update/rollback procedure.
```

The example output is illustrative, not reusable evidence. Replace it with what you observe. A failed first attempt can be valuable evidence when it is safely diagnosed and the final verification passes.
