# Save this as a temporary script and run it
$SSH_KEY = "$env:USERPROFILE\secrets\staging_id_ed25519"
$HOST = "34.11.189.71"
$USER = "ubuntu"  # Change this to your actual SSH user

# Test SSH connection
Write-Host "Testing SSH connection to $HOST..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $USER@$HOST "echo 'Connection successful!'"

# Check if .env.staging exists
Write-Host "
Checking for .env.staging..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $USER@$HOST "ls -la ~/app/deploy/staging/.env.staging 2>&1 || echo 'FILE_NOT_FOUND'"
