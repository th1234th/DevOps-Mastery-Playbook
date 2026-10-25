# Containerization with Docker

## Build challenge

Containerize a small HTTP service. Make the image reproducible and run as a non-root user. Keep build tools out of the runtime image with a multi-stage build where it helps.

## Review checklist

- Pin base images to a deliberate version or digest and establish an update process.
- Use a minimal runtime image, a non-root user, and a read-only filesystem where compatible.
- Add a `.dockerignore`; do not copy credentials, local caches, or source-control metadata into the build context.
- Use exec-form `ENTRYPOINT`/`CMD` so signals reach the application.
- Expose only required ports; do not bake runtime configuration or secrets into image layers.
- Scan the image, understand findings, and rebuild from patched dependencies rather than suppressing findings blindly.
- Test the image as the same user and with constraints similar to production.

## Exercise

Build once, run locally with a non-root UID, then inspect the image layers and SBOM. Record image size, known limitations, health-check behavior, and the exact rebuild command. Compare a one-stage and multi-stage build if the language toolchain is large.

Use the [official Docker documentation](https://docs.docker.com/) for current build and runtime options.