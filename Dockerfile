# syntax=docker/dockerfile:1.9
ARG PY_VERSION="3.12.5"
FROM python:${PY_VERSION}-slim-bookworm as base

ENV AWS_DEFAULT_REGION ap-northeast-1
ENV PROJECT_DIR app
WORKDIR /${PROJECT_DIR}

RUN --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && apt-get install -y \
    pipx libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY uv.lock pyproject.toml README.md ./

# Reference: https://github.com/astral-sh/uv-docker-example/tree/main
RUN --mount=type=cache,target=/root/.cache \
    set -ex && \
    cd /app && \
    uv sync --frozen --no-install-project

ENV PATH=/${PROJECT_DIR}/.venv/bin:$PATH

COPY src ./src
