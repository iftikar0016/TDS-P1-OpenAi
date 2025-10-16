#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# API endpoint
API_URL="http://localhost:8000/api-endpoint"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Web App Generator API - Test Suite            ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo ""

# Test 1: Round 1 - Initial Build
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 TEST 1: Round 1 - Initial Build & Deployment${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Request:${NC}"
cat test_round1.json | jq '.'
echo ""
echo -e "${BLUE}Sending request...${NC}"
echo ""

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d @test_round1.json \
  -w "\n\n${GREEN}HTTP Status: %{http_code}${NC}\n" \
  -s | jq '.'

echo ""
echo -e "${BLUE}Expected Results:${NC}"
echo "  ✓ New repository 'hello-world-app' created on GitHub"
echo "  ✓ index.html, LICENSE, README.md committed"
echo "  ✓ GitHub Pages enabled"
echo "  ✓ Evaluation sent to https://httpbin.org/post"
echo ""
echo -e "${YELLOW}Repository URL: ${NC}https://github.com/AlamIftikar/hello-world-app"
echo -e "${YELLOW}GitHub Pages URL: ${NC}https://AlamIftikar.github.io/hello-world-app/"
echo ""

read -p "Press Enter to continue to Round 2 test (or Ctrl+C to stop)..."
echo ""

# Test 2: Round 2 - Revision
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🔄 TEST 2: Round 2 - Revision & Update${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Request:${NC}"
cat test_round2.json | jq '.'
echo ""
echo -e "${BLUE}Sending request...${NC}"
echo ""

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d @test_round2.json \
  -w "\n\n${GREEN}HTTP Status: %{http_code}${NC}\n" \
  -s | jq '.'

echo ""
echo -e "${BLUE}Expected Results:${NC}"
echo "  ✓ Existing repository 'hello-world-app' fetched"
echo "  ✓ Current index.html retrieved and updated with new features"
echo "  ✓ Rainbow animation, click counter, dark mode added"
echo "  ✓ README.md updated for Round 2"
echo "  ✓ Evaluation sent to https://httpbin.org/post"
echo ""
echo -e "${YELLOW}Repository URL: ${NC}https://github.com/AlamIftikar/hello-world-app"
echo -e "${YELLOW}GitHub Pages URL: ${NC}https://AlamIftikar.github.io/hello-world-app/"
echo ""
echo -e "${GREEN}✅ Test suite completed!${NC}"
echo ""
