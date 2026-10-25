# Production-Ready Container Image Lab

## Scenario and boundary

Package a small HTTP service as a reproducible, non-root image, then run it under production-like local restrictions. This is a single-container deployment exercise; it does not publish an image or require a registry. Only use the image and container name created here.

## Prerequisites

- Docker Engine, Python 3.10+, Git, and `curl`.
- Run commands from the repository root. No root-in-container, host networking, Docker socket mount, credentials, or cloud account is needed.

## Tasks

1. Run the unit tests before building. Explain what `/`, `/healthz`, and an unknown path return.
2. Build the image with a stable local tag and inspect the image ID, configured user, exposed port, health check, and image size.
3. Run it as UID/GID 10001 with a read-only root filesystem, all Linux capabilities dropped, `no-new-privileges`, bounded memory/CPU/PIDs, and a loopback-only host port.
4. Verify the health endpoint, JSON version response, non-root identity, and Docker health status. Inspect logs and container resource configuration.
5. Test one safe failure: request a missing route and verify the service returns 404 without crashing. Stop and remove only the named lab container.
6. Record the image ID, test evidence, limits, rollback command, and production follow-ups (digest pinning, scanning/SBOM, deployment identity, network policy, monitoring, and patch cadence).

## Worked Answer

Run the tests and build:

```sh
python3 -m unittest discover -s 02-containerization/docker/production-image-lab/app -p 'test_*.py' -v
docker build --pull -t image-lab:1.0.0 02-containerization/docker/production-image-lab
docker image inspect image-lab:1.0.0 --format 'id={{.Id}} user={{.Config.User}} ports={{json .Config.ExposedPorts}} healthcheck={{json .Config.Healthcheck}}'
docker image ls image-lab:1.0.0
```

Expected image user is `10001:10001`; its health check calls `/healthz`. Build output and image ID are environment-specific, so record your own results rather than copying a sample digest.

Run with explicit resource and filesystem constraints:

```sh
docker run -d --rm \
  --name image-lab \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --pids-limit 64 \
  --memory 128m \
  --cpus 0.5 \
  --publish 127.0.0.1:18080:8080 \
  image-lab:1.0.0
```

Verify behavior and runtime identity:

```sh
for attempt in $(seq 1 30); do
  HEALTH_STATUS="$(docker inspect image-lab --format '{{.State.Health.Status}}')"
  [ "$HEALTH_STATUS" = healthy ] && break
  [ "$HEALTH_STATUS" = unhealthy ] && { docker logs image-lab; exit 1; }
  sleep 1
done
test "$(docker inspect image-lab --format '{{.State.Health.Status}}')" = healthy
curl -fsS http://127.0.0.1:18080/healthz
curl -fsS http://127.0.0.1:18080/
docker exec image-lab id
docker inspect image-lab --format 'health={{.State.Health.Status}} memory={{.HostConfig.Memory}} cpu={{.HostConfig.NanoCpus}} read_only={{.HostConfig.ReadonlyRootfs}}'
docker logs image-lab
```

Expected: `healthz` returns `ok`; `/` returns JSON with service `image-lab` and version `1.0.0`; UID/GID are 10001; root filesystem is read-only; configured memory is 134217728 bytes and CPU is 500000000 nanocpus. Health may initially be `starting`, so inspect again after a probe interval.

Verify a client error does not stop the service, then clean up:

```sh
if curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18080/not-a-route | grep -qx 404; then
  printf 'Expected 404 observed.\n'
else
  printf 'Unexpected response.\n' >&2
  exit 1
fi
curl -fsS http://127.0.0.1:18080/healthz
docker stop image-lab
```

For this local lab the rollback is `docker run ... image-lab:<previous-tag>` after verifying that image tag/ID. In a production deployment, rollback should target an approved immutable digest through the deployment controller, not a mutable `latest` tag.

## Acceptance and Further Production Work

- Three unit tests pass and the image runs as a non-root numeric UID.
- HTTP health and failure behavior are verified from outside the container.
- Root filesystem is read-only; Linux capabilities are dropped; the process has resource/PID limits; host port binds only to loopback.
- No credentials, source tree, `.git`, or test files are copied into the image.
- Capture the digest and attach an SBOM/scan result in CI. Pin the base image by digest under a reviewed update policy before production.
- Add real service-specific metrics/traces, readiness semantics, graceful shutdown, orchestration health checks, and a tested deployment rollback before calling the service production ready.

## Cleanup

The `docker run` command uses `--rm`; after `docker stop image-lab`, the named lab container is removed automatically. Keep or remove the local image according to your workstation policy; do not use broad prune commands for this exercise.
