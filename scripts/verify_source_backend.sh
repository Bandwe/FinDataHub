#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:5002}"

curl --fail --silent --show-error "$BASE_URL/health" >/dev/null
curl --fail --silent --show-error "$BASE_URL/" >/dev/null
curl --fail --silent --show-error "$BASE_URL/api/companies/all" >/dev/null
curl --fail --silent --show-error "$BASE_URL/api/profit_rate?page=1&per_page=3" >/dev/null

echo "FinDataHub source backend verified at $BASE_URL"
