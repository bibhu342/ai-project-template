# Deployment Runbook

Simple, operational steps for deploying, rolling back, checking logs, handling migrations, and cleaning disk. Use this as an internal checklist.

## Table of Contents

- [Deployment modes](#deployment-modes)
- [Deploy via tag (recommended)](#deploy-via-tag-recommended)
- [Rollback commands](#rollback-commands)
- [SSH + Docker logs checklist](#ssh--docker-logs-checklist)
- [Migration safety steps](#migration-safety-steps)
- [Disk cleanup](#disk-cleanup)
- [Staging vs Production: current and future path](#staging-vs-production-current-and-future-path)
- [Local development](#local-development)
- [Quick smoke test after deploy](#quick-smoke-test-after-deploy)

---

### Deployment modes

The system supports three deploy paths:

| Mode                     | Purpose                   | Trigger           | Notes                                |
| ------------------------ | ------------------------- | ----------------- | ------------------------------------ |
| Semantic tags (`vX.Y.Z`) | Normal releases           | Manual tag + push | CI deploys, migrations run           |
| `latest` + Watchtower    | Fast iteration in staging | Push to `main`    | Auto-pulls only `latest` tag         |
| Manual pull              | Hotfix / rollback         | SSH → pull + up   | Used when CI skipped or in incidents |

Always prefer **tag → CI → staging → verify → promote** for production safety.

## Deploy via tag (recommended)

Applies to images published at: `ghcr.io/bibhu342/ai-project-template:<tag>`

1. Bump and tag

- Update the app version (if applicable) and commit.
- Create a tag locally and push tags:

```powershell
# Local (Windows PowerShell)
git tag v0.1.22
git push --tags
```

2. CI build & push

- GitHub Actions builds the Docker image and pushes to GHCR as `:latest` and `:v0.1.22`.
- Verify the workflow completed in GitHub Actions.

3. Staging auto-update (Watchtower)

- Watchtower on staging pulls the new tag and restarts the API container.
- If auto-update is disabled, pull and restart manually:

```powershell
# Remote (over SSH)
ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP> `
  "docker compose pull api && docker compose up -d api"
```

4. Verify staging

- Health: `/api/health` should return 200.
- Metrics: `/api/metrics` should return Prometheus text.
- Logs: no migration errors, application serves traffic.

```powershell
# From local: quick checks
Invoke-WebRequest https://<staging-host>/api/health
Invoke-WebRequest https://<staging-host>/api/metrics
```

### Quick smoke test after deploy

curl -sf https://<host>/api/health || echo "Health FAIL"
curl -sf https://<host>/api/docs > /dev/null && echo "Docs OK"

5. Promote to production

- Preferred: update production to the same explicit tag (not `latest`).
- If using Watchtower in prod, ensure image tag is pinned (disable `latest`) to avoid surprise rollouts.

```powershell
# Remote to production host
ssh -i "$env:USERPROFILE\secrets\prod_id_ed25519" admin@<PROD_IP> `
  "docker compose pull api && docker compose up -d api"
```

---

## Rollback commands

When a deploy causes issues, pin the previous known-good tag and (if necessary) downgrade schema.

1. Pin previous image

```powershell
# Edit docker-compose.yml on the server to set the previous tag, e.g.:
#   image: ghcr.io/bibhu342/ai-project-template:0.1.21
# Then apply:
ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP> `
  "docker compose pull api && docker compose up -d api"
```

2. Optional: stop auto-updates during rollback

```powershell
# Stop Watchtower temporarily (if running)
ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP> "docker stop watchtower || true"
```

3. Schema downgrade (use with caution)

```powershell
# Step back one migration at a time if current app requires older schema
ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP> `
  "docker compose exec api alembic downgrade -1"
```

4. Validate post-rollback

- Health/metrics ok, logs stable, critical endpoints function.

---

## SSH + Docker logs checklist

Use these quick commands to triage.

```powershell
# SSH into the server (PowerShell)
ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP>
```

Once on the server (bash):

```bash
# Containers up?
docker ps

# Images present?
docker images | grep ai-project-template

# API logs
docker logs --tail 200 api

# Postgres logs (if named postgres)
docker logs --tail 200 postgres

# Current Alembic revision (inside Postgres)
docker exec <postgres-container> psql -U postgres -d ai_lab -c 'SELECT version_num FROM alembic_version;'

# App health from server
curl -sf https://<staging-host>/api/health || echo FAILED
```

From local (PowerShell), one-off checks without interactive SSH:

```powershell
ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP> `
  "docker ps --format '{{.Names}} {{.Image}} {{.Status}}'"

ssh -i "$env:USERPROFILE\secrets\staging_id_ed25519" bibhu342@<STAGING_IP> `
  "docker exec <postgres-container> psql -U postgres -d ai_lab -c 'SELECT version_num FROM alembic_version;'"
```

---

## Migration safety steps

- Always generate migrations explicitly and review the diff.
- Test migrations locally (SQLite in tests; for full fidelity, a local Postgres instance is ideal).
- Stage first: deploy to staging, verify `alembic_version`, and run smoke tests.
- Backups: take a database snapshot/backup before applying destructive migrations.
- Entry point runs `alembic upgrade head` on container start; consider setting `SKIP_MIGRATIONS=1` after initial bootstrap, and run migrations manually during maintenance windows for high-risk changes.
- Never rewrite applied migrations; create a follow-up migration to fix issues.
- Long-running migrations: perform in off-peak or maintenance windows; use additive/online techniques where possible.

Validation on staging after migration:

- Health is 200, metrics emit normally, error rate steady.
- Key endpoints succeed (auth, customers list, notes list/search/pagination).
- Check `alembic_version` and a few representative queries.

---

## Disk cleanup

Check usage and prune safely.

```bash
# Check usage
docker system df

# Remove dangling images only
docker image prune -f

# Remove stopped containers (safe)
docker container prune -f

# Remove unused networks (safe)
docker network prune -f

# Remove unused volumes (DANGEROUS – data loss)
# Only use if you understand the impact.
docker volume prune -f

# Clear builder cache
docker builder prune -f
```

Also consider removing old log files and rotating logs at the host level if disk pressure persists.

---

## Staging vs Production: current and future path

Current (Staging):

- Watchtower auto-updates the API container when a new tag is pushed to GHCR.
- Entrypoint runs `alembic upgrade head` to keep schema current.
- Caddy fronts the API with HTTPS and simple routing.

Production (near-term recommendation):

- Pin explicit image tags (avoid `latest`), update via `docker compose pull && up -d`.
- Keep Watchtower disabled or scoped with filters; prefer manual promotion after verification in staging.
- Maintain regular, automated DB backups and a tested restore procedure.

Future improvements:

- Blue/Green or Canary deployments with Caddy routing switch.
- Manual approval gate in CI for production promotion.
- Read replicas for Postgres and connection pooling.
- Structured logging with trace IDs and OpenTelemetry.
- Define SLOs (availability, latency) and alerting tied to error budgets.

### Local development

# Run API locally

uvicorn app.main:app --reload --port 8000

# Start local Postgres (if using docker compose dev file)

docker compose -f docker-compose.dev.yml up db

# Apply migrations locally

alembic upgrade head
