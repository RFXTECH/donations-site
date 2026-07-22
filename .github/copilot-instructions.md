This repository is a small Flask app deployed to Kubernetes. Keep changes minimal, practical, and consistent with the current architecture unless the user explicitly asks for a larger refactor.

Project-specific guidance:

- The active application logic and both HTML views live in `app.py` as inline `render_template_string` templates. Prefer small, local edits there unless a requested change clearly justifies introducing template files or more modules.
- The public flow currently includes `/` for the gallery, `/upload` for adding new items, `/claim/<id>` for claiming an item, and `/uploads/<filename>` for serving uploaded images. Preserve those flows unless the user asks to change routing behavior.
- State is no longer in-memory. The app stores items in a SQLite database and writes uploads to a filesystem data directory. Do not describe the app as durable beyond the mounted filesystem unless you are explicitly changing persistence guarantees.
- `app.py` currently derives `DATA_DIR` from `/app/data` when that path exists, otherwise it falls back to the current working directory. If touching storage behavior, keep `DATA_DIR`, `UPLOAD_FOLDER`, `DB_PATH`, the Docker image, and Kubernetes volume mounts aligned.
- The database schema is created in `init_db()` inside `app.py` and currently includes `items` with image filename, description, timestamp, claim metadata, and claimed status. Prefer lightweight schema-compatible changes over introducing a migration system unless the user asks for one.
- There is no active authentication flow in the current upload route. Do not assume admin login, sessions, or secret-key based protection exist unless you verify and add them.
- The container image is intentionally simple: `Dockerfile` installs Flask directly and copies only `app.py`. If code changes require more files or dependencies, update `Dockerfile` in the same change so the container still builds.
- The app listens on port `8080`. Keep the Flask runtime port, container port, Service target port, and Ingress expectations aligned when making deployment changes.
- There are two overlapping Kubernetes manifest files, `deployment.yaml` and `k8s-manifests.yaml`, and they are not fully consistent today. When making Kubernetes changes, inspect both files, preserve the intended deployment behavior, and keep them aligned unless the user explicitly wants consolidation.
- The GitHub Actions workflow in `.github/workflows/deploy.yml` builds and pushes the lowercase GHCR image tag for this repository, which resolves to `ghcr.io/rfxtech/donations-site:latest` for the current repo. If image names, registry paths, or deployment expectations change, update the workflow and manifests together.
- `fixed_app.py` and `temp_app.py` are present as alternate or scratch variants, but `app.py` is the active runtime entrypoint. Do not edit or rely on those alternates unless the user explicitly asks.
- `api/` and `public/uploads/` exist in the repo but are not part of the current Flask runtime path unless wired in by code. Do not assume they are active without verifying usage first.

Working style:

- Favor root-cause fixes over cosmetic edits, but avoid introducing unnecessary frameworks or abstractions into this repo.
- Preserve the current lightweight single-file Flask style unless the user explicitly asks for restructuring.
- When possible, validate changes with a narrow local check such as running `python app.py`, checking edited deployment files for consistency, or verifying any path/persistence changes against the current Docker and Kubernetes configuration.