#!/bin/bash

# ============================================
# AI Supervisor System - Complete Test Script
# ============================================
# This script tests all components of your Phase 1 system

API_URL="http://localhost:8000"
FRONTEND_FILE="frontend/supervisor-ui.html"

echo "========================================"
echo "🧪 AI Supervisor System - Test Suite"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ -n "$data" ]; then
        response=$(curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\n%{http_code}")
    else
        response=$(curl -s -X $method "$API_URL$endpoint" -w "\n%{http_code}")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "   Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# ============================================
# 1️⃣  Backend Health Check
# ============================================
echo "1️⃣  Backend Health Checks"
echo "-----------------------------------"

test_endpoint "Health endpoint" "GET" "/health"
test_endpoint "Root endpoint" "GET" "/"
echo ""

# ============================================
# 2️⃣  Knowledge Base Tests
# ============================================
echo "2️⃣  Knowledge Base Tests"
echo "-----------------------------------"

test_endpoint "Get all knowledge" "GET" "/api/knowledge/"
test_endpoint "Search knowledge" "GET" "/api/knowledge/search?query=hours&limit=5"

# Create new knowledge entry
NEW_KNOWLEDGE='{
  "question": "Test question from script?",
  "answer": "This is a test answer",
  "category": "test",
  "keywords": ["test", "script"]
}'
test_endpoint "Create knowledge entry" "POST" "/api/knowledge/" "$NEW_KNOWLEDGE"
echo ""

# ============================================
# 3️⃣  Help Request Tests
# ============================================
echo "3️⃣  Help Request Tests"
echo "-----------------------------------"

HELP_REQUEST='{
  "customer_phone": "7564073505",
  "customer_name": "Aanchal",
  "question": "Who's Salon is this?",
  "context": "Automated testing"
}'

echo -n "Creating help request... "
response=$(curl -s -X POST "$API_URL/api/help-requests/" \
    -H "Content-Type: application/json" \
    -d "$HELP_REQUEST" \
    -w "\n%{http_code}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" -eq 201 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    REQUEST_ID=$(echo "$body" | grep -o '"request_id":"[^"]*"' | cut -d'"' -f4)
    echo "   Request ID: $REQUEST_ID"
else
    echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    REQUEST_ID=""
fi

test_endpoint "Get all help requests" "GET" "/api/help-requests/"
test_endpoint "Get pending requests" "GET" "/api/help-requests/?status=pending"

if [ -n "$REQUEST_ID" ]; then
    echo -n "Resolving help request... "
    RESOLUTION='{
      "supervisor_answer": "This is an automated test answer. The system is working correctly!",
      "supervisor_id": "test_script"
    }'
    response=$(curl -s -X POST "$API_URL/api/supervisor/$REQUEST_ID/resolve" \
        -H "Content-Type: application/json" \
        -d "$RESOLUTION" \
        -w "\n%{http_code}")
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠ SKIPPED${NC} - No request ID available"
fi
echo ""

# ============================================
# 4️⃣  Dashboard Stats Tests
# ============================================
echo "4️⃣  Dashboard Stats Tests"
echo "-----------------------------------"
test_endpoint "Get dashboard stats" "GET" "/api/supervisor/dashboard/stats"
echo ""

# ============================================
# 5️⃣  Frontend Check
# ============================================
echo "5️⃣  Frontend Checks"
echo "-----------------------------------"

if [ -f "$FRONTEND_FILE" ]; then
    echo -e "${GREEN}✓ Frontend file exists${NC} ($FRONTEND_FILE)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    if grep -q "localhost:8000" "$FRONTEND_FILE"; then
        echo -e "${GREEN}✓ API URL configured${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - API URL might not be configured"
    fi
else
    echo -e "${RED}✗ Frontend file not found${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# ============================================
# 6️⃣  Final Summary
# ============================================
echo "========================================"
echo "📊 Test Results Summary"
echo "========================================"
echo ""
echo "Total Tests Run: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}✓ Passed: $TESTS_PASSED${NC}"
echo -e "${RED}✗ Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Your AI Supervisor System is working correctly."
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo "Please check:"
    echo "  1. Backend is running (python run.py)"
    echo "  2. Firebase is configured correctly"
    echo "  3. Check logs for detailed errors"
fi
