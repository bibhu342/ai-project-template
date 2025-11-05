# 🚀 Staging Deployment - Quick Start

## What Was Created

### 1. Docker Compose Stack (`deploy/staging/docker-compose.yml`)

- **API Service**: Pulls from GHCR (`ghcr.io/bibhu342/ai-project-template`)
- **PostgreSQL**: With persistent volume
- **Caddy**: Reverse proxy with automatic HTTPS (Let's Encrypt)
- **Watchtower**: Auto-updates containers every 5 minutes

### 2. Caddy Configuration (`deploy/staging/Caddyfile`)

- Automatic HTTPS with Let's Encrypt
- Security headers (HSTS, X-Frame-Options, etc.)
- Health check monitoring
- Request logging

### 3. Environment Configuration (`.env.staging.example`)

- Template for staging environment variables
- Database credentials
- Domain configuration
- Watchtower notifications

### 4. Smoke Tests (`deploy/staging/smoke.sh`)

- Health endpoint validation
- Root endpoint check
- CRUD operations test (customers)
- Automatic cleanup

### 5. GitHub Actions Workflow (`.github/workflows/deploy-staging.yml`)

- Triggers on tag push (e.g., `v1.0.0-staging`)
- SSH deployment to staging server
- Runs database migrations
- Deploys new version
- Runs smoke tests
- **Automatic rollback on failure**

## 📋 Setup Checklist

### On GitHub (Repository Settings → Secrets)

Add these secrets:

```
Required:
- STAGING_HOST          # your-server-ip or staging.example.com
- STAGING_USER          # ubuntu / deploy / your-ssh-user
- STAGING_SSH_KEY       # Private SSH key (entire content)
- STAGING_DOMAIN        # staging.yourdomain.com
- POSTGRES_PASSWORD     # Secure database password

Optional:
- ACME_EMAIL           # your@email.com
```

### On Staging Server

1. **Install Docker**

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Setup SSH Key**

   ```bash
   # Add GitHub Actions public key to authorized_keys
   echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

3. **Configure DNS**

   - Add A record: `staging.yourdomain.com → your-server-ip`
   - Wait for DNS propagation (can take 5-60 minutes)

4. **Open Firewall Ports**

   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP (ACME challenge)
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

5. **Create Environment File**
   ```bash
   mkdir -p ~/ai-project-template/deploy/staging
   cd ~/ai-project-template/deploy/staging
   # Copy .env.staging.example from repo and edit
   nano .env.staging
   ```

## 🚀 Deploy

### Option 1: Tag-based Deployment (Recommended)

```bash
# Create and push a staging tag
git tag v1.0.0-staging
git push origin v1.0.0-staging
```

### Option 2: Manual Trigger

1. Go to GitHub → Actions → "Deploy to Staging"
2. Click "Run workflow"
3. Enter image tag (e.g., `main`, `v1.0.0`)
4. Click "Run workflow"

## 🔄 Deployment Flow

```
1. 📦 Pull latest image from GHCR
2. 💾 Backup current deployment
3. 🗄️  Run database migrations (alembic upgrade head)
4. 🚀 Deploy new version
5. ⏳ Wait for health checks (max 2 minutes)
6. 🧪 Run smoke tests
7. ✅ Success → Keep deployment
   ❌ Failure → Automatic rollback to backup
```

## 🧪 Test Deployment

```bash
# SSH to staging server
ssh $STAGING_USER@$STAGING_HOST

# Check services
cd ~/ai-project-template/deploy/staging
docker compose ps

# View logs
docker compose logs -f api

# Run smoke tests manually
./smoke.sh https://staging.yourdomain.com

# Check SSL certificate
curl -I https://staging.yourdomain.com
```

## 📊 Monitoring

### Check Service Health

```bash
curl https://staging.yourdomain.com/health
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f caddy
docker compose logs -f postgres
```

### Database Backup

```bash
docker compose exec postgres pg_dump -U postgres ai_lab > backup.sql
```

## 🔧 Manual Operations

### Update Image Manually

```bash
cd ~/ai-project-template/deploy/staging
docker compose pull api
docker compose up -d
```

### Restart Service

```bash
docker compose restart api
```

### Rollback to Previous Version

```bash
# List backup images
docker images | grep backup-

# Set backup tag in .env.staging
export IMAGE_TAG=backup-20250106-143000

# Restart
docker compose down
docker compose up -d
```

## 🔒 Security Notes

1. **Strong Passwords**: Use `openssl rand -base64 32`
2. **Firewall**: Only expose 22, 80, 443
3. **SSH Keys**: Use ed25519 keys, disable password auth
4. **SSL**: Caddy auto-provisions Let's Encrypt certificates
5. **Updates**: Watchtower auto-updates containers

## 📚 Documentation

Full documentation available in:

- `deploy/staging/README.md` - Complete deployment guide
- `.env.staging.example` - Environment variables reference
- `smoke.sh` - Smoke test details

## 🆘 Troubleshooting

### Deployment Fails

```bash
# Check GitHub Actions logs
# On server, check service logs:
docker compose logs api

# Verify environment variables
docker compose config
```

### SSL Certificate Issues

```bash
# Check Caddy logs
docker compose logs caddy

# Verify DNS
nslookup staging.yourdomain.com

# Test ACME challenge
curl http://staging.yourdomain.com/.well-known/acme-challenge/test
```

### Database Connection Issues

```bash
# Check PostgreSQL health
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U postgres -d ai_lab
```

## ✅ What's Next?

1. ✅ Configure GitHub Secrets
2. ✅ Setup staging server
3. ✅ Configure DNS
4. ✅ Push a tag to deploy
5. ✅ Monitor first deployment
6. ✅ Test with smoke.sh
7. 🎉 Your app is live!

---

**Ready to deploy?** Just push a tag:

```bash
git tag v1.0.0-staging
git push origin v1.0.0-staging
```

Then watch the magic happen in GitHub Actions! 🚀
