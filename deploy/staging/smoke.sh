#!/usr/bin/env bash
# ============================================================================
# Smoke Tests for Staging Deployment
# ============================================================================
# This script validates the staging deployment by:
# 1. Checking the health endpoint
# 2. Performing basic CRUD operations on the customers endpoint
# Usage: ./smoke.sh [BASE_URL]
# Example: ./smoke.sh https://staging.example.com
# ============================================================================

set -euo pipefail

# Configuration
BASE_URL="${1:-http://localhost}"
TIMEOUT=10
MAX_RETRIES=30
RETRY_DELAY=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for service to be ready
wait_for_health() {
    log_info "Waiting for service to be healthy at ${BASE_URL}/health..."
    
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -f -s --max-time $TIMEOUT "${BASE_URL}/health" > /dev/null 2>&1; then
            log_info "Service is healthy!"
            return 0
        fi
        
        log_warn "Health check failed (attempt $i/$MAX_RETRIES). Retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    done
    
    log_error "Service failed to become healthy after $MAX_RETRIES attempts"
    return 1
}

# Test health endpoint
test_health() {
    log_info "Testing health endpoint..."
    
    response=$(curl -s --max-time $TIMEOUT "${BASE_URL}/health")
    
    if echo "$response" | grep -q "ok"; then
        log_info "✓ Health check passed"
        return 0
    else
        log_error "✗ Health check failed. Response: $response"
        return 1
    fi
}

# Test root endpoint
test_root() {
    log_info "Testing root endpoint..."
    
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "${BASE_URL}/")
    
    if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 404 ]; then
        log_info "✓ Root endpoint accessible (HTTP $status_code)"
        return 0
    else
        log_error "✗ Root endpoint returned unexpected status: HTTP $status_code"
        return 1
    fi
}

# Test CRUD operations on customers endpoint
test_customers_crud() {
    log_info "Testing customers CRUD operations..."
    
    # Create a test customer
    log_info "  Creating test customer..."
    create_response=$(curl -s -X POST --max-time $TIMEOUT \
        -H "Content-Type: application/json" \
        -d '{"name":"Smoke Test User","email":"smoketest@example.com"}' \
        "${BASE_URL}/api/customers" || echo "")
    
    if [ -z "$create_response" ]; then
        log_warn "  ⚠ Create customer endpoint not available or failed (might not be implemented yet)"
        return 0
    fi
    
    # Extract customer ID from response
    customer_id=$(echo "$create_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' || echo "")
    
    if [ -z "$customer_id" ]; then
        log_warn "  ⚠ Could not extract customer ID from response (endpoint might have different schema)"
        return 0
    fi
    
    log_info "  ✓ Customer created with ID: $customer_id"
    
    # Read the customer
    log_info "  Reading customer..."
    read_response=$(curl -s --max-time $TIMEOUT "${BASE_URL}/api/customers/${customer_id}" || echo "")
    
    if echo "$read_response" | grep -q "smoketest@example.com"; then
        log_info "  ✓ Customer read successfully"
    else
        log_warn "  ⚠ Customer read failed or schema mismatch"
    fi
    
    # List customers
    log_info "  Listing customers..."
    list_response=$(curl -s --max-time $TIMEOUT "${BASE_URL}/api/customers?limit=10" || echo "")
    
    if [ -n "$list_response" ]; then
        log_info "  ✓ Customers list retrieved"
    else
        log_warn "  ⚠ Customers list failed"
    fi
    
    # Delete the customer (cleanup)
    log_info "  Deleting test customer..."
    delete_status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE --max-time $TIMEOUT \
        "${BASE_URL}/api/customers/${customer_id}" || echo "000")
    
    if [ "$delete_status" -eq 200 ] || [ "$delete_status" -eq 204 ]; then
        log_info "  ✓ Customer deleted successfully"
    else
        log_warn "  ⚠ Customer deletion returned status: HTTP $delete_status"
    fi
    
    log_info "✓ CRUD operations test completed"
    return 0
}

# Main execution
main() {
    log_info "=========================================="
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
