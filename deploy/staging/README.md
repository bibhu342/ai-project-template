# Staging Deployment Guide

This directory contains the staging deployment configuration for the AI Project Template.

## 🏗️ Architecture

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │ HTTPS (443)
┌──────▼──────┐
│   Caddy     │ ← Automatic HTTPS via Let's Encrypt
│ (Reverse    │
│  Proxy)     │
└──────┬──────┘
       │
┌──────▼──────┐
│   FastAPI   │ ← Docker image from GHCR
│     API     │
└──────┬──────┘
       │
┌──────▼──────┐
│  PostgreSQL │ ← Persistent volume
│  Database   │
└─────────────┘

┌─────────────┐
│ Watchtower  │ ← Auto-updates from GHCR
└─────────────┘
```

## 📋 Prerequisites

### On Your Staging Server

1. **Docker & Docker Compose**

   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   sudo apt-get install docker-compose-plugin
   ```

2. **DNS Configuration**

   - Point your domain (e.g., `staging.yourdomain.com`) to your server's IP address
   - Create an A record: `staging.yourdomain.com → your-server-ip`

3. **Firewall Rules**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP (for ACME challenge)
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

### In GitHub Repository

Configure these secrets in **Settings → Secrets and variables → Actions → Secrets**:

#### Required Secrets

| Secret Name         | Description                     | Example                                  |
| ------------------- | ------------------------------- | ---------------------------------------- |
| `STAGING_HOST`      | Your staging server IP/hostname | `staging.example.com` or `192.168.1.100` |
| `STAGING_USER`      | SSH username on staging server  | `deploy` or `ubuntu`                     |
| `STAGING_SSH_KEY`   | Private SSH key for deployment  | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `STAGING_DOMAIN`    | Your staging domain             | `staging.example.com`                    |
| `POSTGRES_PASSWORD` | Database password               | `your-secure-password`                   |

#### Optional Secrets

| Secret Name                   | Description                                        |
| ----------------------------- | -------------------------------------------------- |
| `ACME_EMAIL`                  | Email for Let's Encrypt notifications              |
| `WATCHTOWER_NOTIFICATION_URL` | Slack/Discord webhook for deployment notifications |

### SSH Key Setup

1. **Generate SSH Key (on your local machine)**

   ```bash
   ssh-keygen -t ed25519 -C "github-actions-staging" -f ~/.ssh/staging_deploy
   ```

2. **Add Public Key to Staging Server**

   ```bash
   # Copy public key
   cat ~/.ssh/staging_deploy.pub

   # On staging server, add to authorized_keys
   ssh user@staging-server
   echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

3. **Add Private Key to GitHub Secrets**
   ```bash
   # Copy private key content
   cat ~/.ssh/staging_deploy
   # Paste entire content (including headers) into STAGING_SSH_KEY secret
   ```

## 🚀 Deployment

### Initial Setup on Staging Server

1. **Create deployment user (optional but recommended)**

   ```bash
   sudo adduser deploy
   sudo usermod -aG docker deploy
   ```

2. **Create environment file**

   ```bash
   cd ~/ai-project-template/deploy/staging
   cp ../../../.env.staging.example .env.staging
   nano .env.staging  # Edit with your values
   ```

3. **Manual first deployment**
   ```bash
   cd ~/ai-project-template/deploy/staging
   docker compose --env-file .env.staging up -d
   ```

### Automated Deployment via GitHub Actions

The deployment workflow (`deploy-staging.yml`) triggers on:

1. **Tag Push** (recommended)

   ```bash
   # Create and push a staging tag
   git tag v1.0.0-staging
   git push origin v1.0.0-staging
   ```

2. **Manual Trigger**
   - Go to Actions → Deploy to Staging → Run workflow
   - Specify image tag (e.g., `main`, `v1.0.0`)

### Deployment Flow

1. ✅ Checkout code
2. ✅ Copy deployment files to server via SSH
3. ✅ Pull latest Docker image from GHCR
4. ✅ **Backup current deployment** (creates backup tag)
5. ✅ **Run database migrations** (`alembic upgrade head`)
6. ✅ Deploy new version
7. ✅ Wait for health checks
8. ✅ **Run smoke tests**
9. ✅ Success → Keep deployment
10. ❌ Failure → **Automatic rollback to backup**

## 🧪 Smoke Tests

The smoke test script (`smoke.sh`) validates:

- ✅ Health endpoint responds with `"ok"`
- ✅ Root endpoint is accessible
- ✅ CRUD operations on customers endpoint
  - Create customer
  - Read customer
  - List customers
  - Delete customer (cleanup)

Run manually:

```bash
cd ~/ai-project-template/deploy/staging
./smoke.sh https://staging.yourdomain.com
```

## 🔄 Watchtower Auto-Updates

Watchtower automatically checks for new images every 5 minutes and updates containers with the `com.centurylinklabs.watchtower.enable=true` label.

### Disable Auto-Updates

To disable auto-updates, remove the Watchtower service from `docker-compose.yml` or set `WATCHTOWER_POLL_INTERVAL=0`.

### Manual Update

```bash
cd ~/ai-project-template/deploy/staging
docker compose pull
docker compose up -d
```

## 📊 Monitoring & Maintenance

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f caddy
docker compose logs -f postgres
```

### Check Service Status

```bash
docker compose ps
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart api
```

### Database Backup

```bash
# Create backup
docker compose exec postgres pg_dump -U postgres ai_lab > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20250106.sql | docker compose exec -T postgres psql -U postgres ai_lab
```

## 🔒 Security Best Practices

1. **Use strong passwords**

   - Generate with: `openssl rand -base64 32`

2. **Enable firewall**

   - Only expose ports 22, 80, 443

3. **Regular updates**

   ```bash
   sudo apt update && sudo apt upgrade -y
   docker compose pull
   docker compose up -d
   ```

4. **Monitor logs**

   - Check Caddy logs: `docker compose logs caddy`
   - Enable Watchtower notifications

5. **SSL/TLS**
   - Caddy automatically provisions Let's Encrypt certificates
   - Certificates auto-renew before expiry

## 🔧 Troubleshooting

### Service won't start

```bash
# Check logs
docker compose logs api

# Check environment variables
docker compose config

# Verify network
docker network ls
docker network inspect staging_app-network
```

### Database connection issues

```bash
# Check PostgreSQL is healthy
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U postgres -d ai_lab -c "\l"

# Check DATABASE_URL format
echo $DATABASE_URL
```

### SSL certificate issues

```bash
# Check Caddy logs
docker compose logs caddy

# Verify DNS points to your server
nslookup staging.yourdomain.com

# Test ACME challenge
curl http://staging.yourdomain.com/.well-known/acme-challenge/test
```

### Rollback manually

```bash
cd ~/ai-project-template/deploy/staging

# List available backup images
docker images | grep backup-

# Update .env.staging with backup tag
export IMAGE_TAG=backup-20250106-143000

# Restart services
docker compose down
docker compose up -d
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Watchtower Documentation](https://containrrr.dev/watchtower/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker compose logs -f`
2. Verify secrets are configured in GitHub
3. Ensure DNS is properly configured
4. Test SSH access: `ssh $STAGING_USER@$STAGING_HOST`
5. Run smoke tests manually: `./smoke.sh`
