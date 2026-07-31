# Donations Site - rfox.net

This repository contains the source code and deployment configuration for the **donations.rfox.net** website.

## Overview

The donations site is a lightweight Flask application designed to provide a landing page for charitable contributions via the RFX Tech ecosystem. It is deployed on the `rfox.net` Kubernetes cluster.

## Architecture

- **Runtime:** Python 3.11-slim
- **Web Framework:** Flask
- **Container Registry:** GitHub Container Registry (GHCR)
- **Orchestration:** Kubernetes
- **Ingress:** Nginx Ingress Controller with TLS via `wildcard-rfox-net-tls`

## Repository structure

- `app.py`: Core Flask application logic
- `Dockerfile`: Container build for the public app
- `requirements.txt`: Python runtime and test dependencies
- `.github/workflows/deploy.yml`: GitHub Actions test/build/push workflow
- `k8s/app.yaml`: Public app Deployment, Service, and Ingress
- `k8s/sqlite-web.yaml`: LAN-only SQLite admin UI manifests
- `tests/test_app.py`: Basic Flask smoke tests

## Deployment workflow

1. Push to `main` triggers GitHub Actions.
2. GitHub Actions builds and pushes `ghcr.io/rfxtech/donations-site:latest`.
3. Keel notices the new image digest in GHCR.
4. Kubernetes rolls out the updated public app.

## Access

- Public site: https://donations.rfox.net
- Internal DB UI: https://donations-db.rfox.net

## Notes

- `donations-db.rfox.net` is LAN-restricted.
- The admin UI is intended for internal maintenance, not public browsing.
