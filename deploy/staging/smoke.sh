#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://api.34.11.189.71.nip.io"
TIMESTAMP=$(date +%s)
EMAIL="smoketest_${TIMESTAMP}@example.com"
PASSWORD="TestPassword123!"

echo "[smoke] Testing health endpoint..."
curl -sf "${BASE_URL}/health" | jq .

echo "[smoke] Registering user ${EMAIL}..."
curl -sf -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
  | jq . || echo "[smoke] Registration failed (may already exist, continuing...)"

echo "[smoke] Logging in..."
LOGIN_RESPONSE=$(curl -sf -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${EMAIL}&password=${PASSWORD}")

TOKEN=$(echo "${LOGIN_RESPONSE}" | jq -r '.access_token')

if [[ -z "${TOKEN}" || "${TOKEN}" == "null" ]]; then
  echo "[smoke] ERROR: Failed to get access token"
  exit 1
fi

echo "[smoke] Got access token: ${TOKEN:0:20}..."

echo "[smoke] Calling /users/me..."
curl -sf "${BASE_URL}/users/me" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq .

echo "[smoke] OK"

