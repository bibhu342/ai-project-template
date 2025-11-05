#!/usr/bin/env bash
# Smoke test script for Docker container
# Tests basic API health and database connectivity

set -e

echo "🔍 Starting smoke tests..."

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
  if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API is responding"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ API failed to start within 30 seconds"
    exit 1
  fi
  sleep 1
done

# Test 1: Health endpoint
echo "🧪 Test 1: Health endpoint"
RESPONSE=$(curl -sf http://localhost:8000/api/health)
if echo "$RESPONSE" | grep -q '"status":"ok"'; then
  echo "✅ Health endpoint OK"
else
  echo "❌ Health endpoint failed"
  echo "Response: $RESPONSE"
  exit 1
fi

# Test 2: Create customer (tests DB connectivity)
echo "🧪 Test 2: Create customer (DB connectivity)"
CREATE_RESPONSE=$(curl -sf -X POST http://localhost:8000/api/customers \
  -H "Content-Type: application/json" \
  -d '{"name":"Smoke Test User","email":"smoke@test.com"}')

if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
  CUSTOMER_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
  echo "✅ Customer created with ID: $CUSTOMER_ID"
else
  echo "❌ Failed to create customer"
  echo "Response: $CREATE_RESPONSE"
  exit 1
fi

# Test 3: Retrieve customer
echo "🧪 Test 3: Retrieve customer"
GET_RESPONSE=$(curl -sf http://localhost:8000/api/customers/$CUSTOMER_ID)
if echo "$GET_RESPONSE" | grep -q '"email":"smoke@test.com"'; then
  echo "✅ Customer retrieved successfully"
else
  echo "❌ Failed to retrieve customer"
  echo "Response: $GET_RESPONSE"
  exit 1
fi

# Test 4: Delete customer (cleanup)
echo "🧪 Test 4: Delete customer (cleanup)"
curl -sf -X DELETE http://localhost:8000/api/customers/$CUSTOMER_ID
echo "✅ Customer deleted"

echo ""
echo "🎉 All smoke tests passed!"
