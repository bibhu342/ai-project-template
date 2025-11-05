# Staging Server Setup Guide

**⚠️ IMPORTANT: Complete ALL steps below BEFORE pushing your first tag!**

The deployment workflow expects:

1. SSH public key in server's `~/.ssh/authorized_keys`
2. Docker installed and accessible without sudo
3. `.env.staging` file with actual passwords at `~/app/deploy/staging/.env.staging`

## Step 1: Add SSH Public Key to Server

SSH into your server at **34.11.189.71** using your current credentials:

```bash
ssh ubuntu@34.11.189.71
# (or whatever user you use)
```

Then run these commands on the server:

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add the GitHub Actions SSH public key
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA1ioF9U2VP5GeYylv8CP8MHFnw8CrGlcS2tVn/4SKEf ai-project-template staging deploy" >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys

# Verify the key was added
tail -1 ~/.ssh/authorized_keys
```

## Step 2: Create .env.staging File

Still on the server, create the directory structure and environment file:

```bash
# Create the directory
mkdir -p ~/app/deploy/staging
cd ~/app/deploy/staging

# Create .env.staging file
cat > .env.staging << 'EOF'
# Docker Image Configuration
IMAGE_NAME=bibhu342/ai-project-template
IMAGE_TAG=latest

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_TO_A_STRONG_PASSWORD
POSTGRES_DB=ai_lab

# Database URL for the API
DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME_TO_A_STRONG_PASSWORD@postgres:5432/ai_lab

# Application Settings (if needed)
# JWT_SECRET=your-jwt-secret-here
# API_HOST=0.0.0.0
# API_PORT=8000
EOF

# Edit the file to set a strong password
nano .env.staging
# Change CHANGE_ME_TO_A_STRONG_PASSWORD to an actual strong password in both places
# Press Ctrl+X, then Y, then Enter to save

# Verify the file exists
ls -la .env.staging
cat .env.staging
```

## Step 3: Install Docker (if not already installed)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install jq (required for smoke tests)
sudo apt-get update && sudo apt-get install -y jq

# Log out and back in for group changes to take effect
exit
```

SSH back in and verify Docker:

```bash
docker --version
docker ps
jq --version
```

## Step 4: Update GitHub Secrets

Update these secrets in GitHub repository settings to match your server:

```powershell
# From your Windows machine, run:
gh secret set STAGING_HOST --env staging --body "34.11.189.71"
gh secret set STAGING_USER --env staging --body "ubuntu"
# (or whatever user you're using)
```

## Step 5: Test the Setup

From your Windows machine:

```powershell
# Test SSH connection with the deploy key
$SSH_KEY = "$env:USERPROFILE\secrets\staging_id_ed25519"
ssh -i $SSH_KEY ubuntu@34.11.189.71 "echo 'SSH works!' && ls -la ~/app/deploy/staging/.env.staging"
```

You should see "SSH works!" and the .env.staging file details.

## Step 6: Deploy!

```powershell
# Tag and push to trigger deployment
git tag v1.0.0
git push origin v1.0.0
```

Monitor the deployment in GitHub Actions:

```powershell
gh run watch
```

## Verification

After deployment completes, test your API:

```powershell
# Health check
curl https://api.34.11.189.71.nip.io/health

# API docs
Start-Process "https://api.34.11.189.71.nip.io/docs"
```

## Troubleshooting

### Deployment fails with ".env.staging not found"

The `.env.staging` file must exist on the server at `~/app/deploy/staging/.env.staging` before the first deployment. It contains secrets and should **NEVER** be committed to git.

To fix:

1. SSH into the server: `ssh ubuntu@34.11.189.71`
2. Create the file:
   ```bash
   mkdir -p ~/app/deploy/staging
   cd ~/app/deploy/staging
   cp .env.staging.example .env.staging  # if the repo is already cloned
   nano .env.staging  # Set your actual passwords
   ```

### Smoke test fails with SSH handshake error

The smoke test (`smoke.sh`) does NOT use SSH - it only makes HTTPS API calls to `https://api.34.11.189.71.nip.io`. If you see SSH errors:

1. Check that the server's SSH service is running: `sudo systemctl status ssh`
2. Verify the GitHub Actions SSH key is in `~/.ssh/authorized_keys` on the server
3. The smoke test itself only needs:
   - The API to be accessible via HTTPS
   - `curl` and `jq` installed on the server

### Check service logs

If deployment fails, SSH into the server and check logs:

```bash
cd ~/app/deploy/staging
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f reverse-proxy
```
