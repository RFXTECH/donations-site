# Donations Site - rfox.net

This repository contains the source code and deployment configuration for the **donations.rfox.net** website.

## 🚀 Overview
The donations site is a lightweight Flask application designed to provide a landing page for charitable contributions via the RFX Tech ecosystem. It is deployed on the `rfox.net` Kubernetes cluster.

## 🏗 Architecture
- **Runtime:** Python 3.11 (slim)
- **Web Framework:** Flask
- **Container Registry:** GitHub Container Registry (GHCR)
- **Orchestration:** Kubernetes (k8s-worker1 & k8s-worker2)
- **Deployment Strategy:** Automated via Keel (Continuous Deployment)
- **Ingress:** Nginx Ingress Controller with TLS via `wildcard-rfox-net-tls`

## 🛠 Deployment Workflow
The deployment is fully automated using GitHub Actions and Keel:
1.  **Developer Push:** A push to the `main` branch triggers a GitHub Action.
2.    **Build & Push:** GitHub Actions builds the Docker image and pushes it to `ghcr.io/rfxtech/donations-site:latest`.
3.  **Auto-Deploy (Keel):** The Keel agent in the Kubernetes cluster detects the new image digest in GHCR by polling every 1 minute.
4.  **Rolling Update:** Keel triggers a rolling update of the `donations-site` deployment using the updated image.

## 📂 Repository Structure
- `app.py`: The core Flask application logic.
- `Dockerfile`: Instructions for building the production container image.
- `.github/workflows/deploy.yml`: GitHub Actions workflow definition.
- `k8s-manifests.yaml`: Kubernetes manifests (Deployment, Service, and Ingress).

## 🌐 Access
The application is publicly accessible at: **[https://donations.rfox.net](https://donations.rfox.net)**
