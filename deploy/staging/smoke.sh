#!/usr/bin/env bash
# ============================================================================
# Smoke Tests for Staging Deployment
# ============================================================================
# This script validates the staging deployment by:
# 1. Checking the health endpoint
# 2. Registering a test user
# 3. Logging in to get a JWT token
# 4. Calling /users/me with the token
# Usage: ./smoke.sh
# ============================================================================

set -euo pipefail

# Configuration
BASE_URL="https://api.34.11.189.71.nip.io"
TEST_EMAIL="smoketest-$(date +%s)@example.com"
TEST_PASSWORD="SmokeTest123!Pass"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[smoke]${NC} $1"
}

log_error() {
    echo -e "${RED}[smoke ERROR]${NC} $1"
}

# 1. Health check
log "Testing health endpoint..."
if ! curl -fsSL "${BASE_URL}/health" > /dev/null; then
    log_error "Health check failed"
    exit 1
fi
log "✓ Health check passed"

# 2. Register user
log "Registering test user ${TEST_EMAIL}..."
register_response=$(curl -fsSL -X POST "${BASE_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASSWORD}\"}")

if ! echo "$register_response" | jq -e '.id' > /dev/null 2>&1; then
    log_error "Registration failed: $register_response"
    exit 1
fi
log "✓ User registered"

# 3. Login to get JWT
log "Logging in..."
login_response=$(curl -fsSL -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${TEST_EMAIL}&password=${TEST_PASSWORD}")

ACCESS_TOKEN=$(echo "$login_response" | jq -r '.access_token')

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
    log_error "Login failed: $login_response"
    exit 1
fi
log "✓ Login successful, token acquired"

# 4. Call /users/me with JWT
log "Fetching current user info..."
me_response=$(curl -fsSL "${BASE_URL}/users/me" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}")

user_email=$(echo "$me_response" | jq -r '.email')

if [ "$user_email" != "$TEST_EMAIL" ]; then
    log_error "/users/me returned unexpected email: $user_email"
    exit 1
fi
log "✓ /users/me returned correct user: $user_email"

echo -e "${GREEN}[smoke] OK${NC}"
    log_info "Starting Smoke Tests"
    log_info "Target: ${BASE_URL}"
    log_info "=========================================="
    echo
    
    # Wait for service
    if ! wait_for_health; then
        log_error "Smoke tests failed: Service not healthy"
        exit 1
    fi
    echo
    
    # Run tests
    test_health || { log_error "Health test failed"; exit 1; }
    echo
    
    test_root || { log_error "Root endpoint test failed"; exit 1; }
    echo
    
    test_customers_crud || { log_warn "CRUD tests had warnings but continuing..."; }
    echo
    
    log_info "=========================================="
    log_info "All Smoke Tests Passed! ✓"
    log_info "=========================================="
    
    exit 0
}

# Run main function
main "$@"
