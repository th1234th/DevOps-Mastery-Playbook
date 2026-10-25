ARG RUNNER_VERSION=2.338.1
FROM ghcr.io/actions/actions-runner:${RUNNER_VERSION} AS base

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git jq python3 \
    && rm -rf /var/lib/apt/lists/*
USER runner
WORKDIR /home/runner

FROM base AS node
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*
USER runner

FROM base AS build
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential golang-go python3-venv \
    && rm -rf /var/lib/apt/lists/*
USER runner