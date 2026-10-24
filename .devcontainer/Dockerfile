# Reproducible development environment (ADR-0003). Python itself is installed by `uv sync`
# from `.python-version`, so the image only needs uv at the version pyproject.toml requires.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /usr/local/bin/
USER vscode
ENV UV_LINK_MODE=copy
