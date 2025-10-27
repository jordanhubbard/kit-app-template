#!/bin/bash
# Comprehensive test for all template types

set -e  # Exit on error

REPO_ROOT="/home/jkh/Src/kit-app-template"
API_BASE="http://localhost:5000/api"

echo "========================================="
echo "Testing All Template Types"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Clean everything first
echo -e "${BLUE}Cleaning all existing projects...${NC}"
curl -X POST "${API_BASE}/projects/clean?include_test=false" -s > /dev/null
echo -e "${GREEN}✓ Clean complete${NC}"
echo ""

# Test 1: Create APPLICATION
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}TEST 1: Create APPLICATION (kit_base_editor)${NC}"
echo -e "${BLUE}=========================================${NC}"

APP_RESPONSE=$(curl -X POST "${API_BASE}/templates/create" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "kit_base_editor",
    "name": "test_app",
    "displayName": "Test Application",
    "version": "1.0.0",
    "standalone": false,
    "perAppDeps": false,
    "enableStreaming": false
  }' -s)

echo "$APP_RESPONSE" | python3 -m json.tool | head -20

APP_SUCCESS=$(echo "$APP_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('success', False))")

if [ "$APP_SUCCESS" = "True" ]; then
    echo -e "${GREEN}✓ Application creation reported success${NC}"
    
    # Verify structure
    if [ -d "${REPO_ROOT}/source/apps/test_app" ]; then
        echo -e "${GREEN}✓ Application directory exists${NC}"
    else
        echo -e "${RED}✗ Application directory missing${NC}"
        exit 1
    fi
    
    if [ -f "${REPO_ROOT}/source/apps/test_app/test_app.kit" ]; then
        echo -e "${GREEN}✓ .kit file exists${NC}"
        echo "  Contents (first 10 lines):"
        head -10 "${REPO_ROOT}/source/apps/test_app/test_app.kit" | sed 's/^/    /'
    else
        echo -e "${RED}✗ .kit file missing${NC}"
        exit 1
    fi
    
    # Check for app-specific structure
    if [ -d "${REPO_ROOT}/source/apps/test_app/data" ]; then
        echo -e "${GREEN}✓ Application data directory exists${NC}"
    fi
else
    echo -e "${RED}✗ Application creation failed${NC}"
    exit 1
fi

echo ""

# Test 2: Create EXTENSION
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}TEST 2: Create EXTENSION (basic_python_extension)${NC}"
echo -e "${BLUE}=========================================${NC}"

EXT_RESPONSE=$(curl -X POST "${API_BASE}/templates/create" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "basic_python_extension",
    "name": "test_extension",
    "displayName": "Test Extension",
    "version": "1.0.0",
    "standalone": false
  }' -s)

echo "$EXT_RESPONSE" | python3 -m json.tool | head -20

EXT_SUCCESS=$(echo "$EXT_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('success', False))")

if [ "$EXT_SUCCESS" = "True" ]; then
    echo -e "${GREEN}✓ Extension creation reported success${NC}"
    
    # Get the actual extension directory from the API response
    EXT_DIR=$(echo "$EXT_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin)['projectInfo']['outputDir'])")
    EXT_FILE=$(echo "$EXT_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin)['projectInfo']['kitFile'])")
    
    # Verify structure (extensions go to different location)
    if [ -d "$EXT_DIR" ]; then
        echo -e "${GREEN}✓ Extension directory exists: ${EXT_DIR}${NC}"
    else
        echo -e "${RED}✗ Extension directory missing: ${EXT_DIR}${NC}"
        # List what's actually there
        echo "Available extensions:"
        ls -1 "${REPO_ROOT}/source/extensions/" | grep test | head -5
        exit 1
    fi
    
    if [ -f "$EXT_FILE" ]; then
        echo -e "${GREEN}✓ extension.toml exists${NC}"
        echo "  Contents (first 10 lines):"
        head -10 "$EXT_FILE" | sed 's/^/    /'
    else
        echo -e "${RED}✗ extension.toml missing: ${EXT_FILE}${NC}"
        exit 1
    fi
    
    # Check for Python files
    if [ -d "${EXT_DIR}/test_extension" ]; then
        echo -e "${GREEN}✓ Python package directory exists${NC}"
    fi
else
    echo -e "${RED}✗ Extension creation failed${NC}"
    exit 1
fi

echo ""

# Test 3: Create MICROSERVICE
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}TEST 3: Create MICROSERVICE (kit_service)${NC}"
echo -e "${BLUE}=========================================${NC}"

SVC_RESPONSE=$(curl -X POST "${API_BASE}/templates/create" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "kit_service",
    "name": "test_service",
    "displayName": "Test Service",
    "version": "1.0.0",
    "standalone": false
  }' -s)

echo "$SVC_RESPONSE" | python3 -m json.tool | head -20

SVC_SUCCESS=$(echo "$SVC_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('success', False))")

if [ "$SVC_SUCCESS" = "True" ]; then
    echo -e "${GREEN}✓ Microservice creation reported success${NC}"
    
    # Verify structure (services also go to apps directory)
    if [ -d "${REPO_ROOT}/source/apps/test_service" ]; then
        echo -e "${GREEN}✓ Microservice directory exists${NC}"
    else
        echo -e "${RED}✗ Microservice directory missing${NC}"
        exit 1
    fi
    
    if [ -f "${REPO_ROOT}/source/apps/test_service/test_service.kit" ]; then
        echo -e "${GREEN}✓ .kit file exists${NC}"
        echo "  Contents (first 10 lines):"
        head -10 "${REPO_ROOT}/source/apps/test_service/test_service.kit" | sed 's/^/    /'
    else
        echo -e "${RED}✗ .kit file missing${NC}"
        exit 1
    fi
    
    # Check for service-specific files
    if [ -d "${REPO_ROOT}/source/apps/test_service/services" ]; then
        echo -e "${GREEN}✓ Services directory exists${NC}"
    fi
else
    echo -e "${RED}✗ Microservice creation failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}FINAL VERIFICATION${NC}"
echo -e "${BLUE}=========================================${NC}"

echo ""
echo "Created structure:"
echo ""
echo "Applications (in source/apps/):"
ls -1d ${REPO_ROOT}/source/apps/*/ 2>/dev/null | grep -v "exts\|extscache" | sed 's|.*/||' | sed 's|/$||' | sed 's/^/  - /'

echo ""
echo "Extensions (in source/extensions/):"
ls -1d ${REPO_ROOT}/source/extensions/my_company.*/ 2>/dev/null | sed 's|.*/||' | sed 's|/$||' | sed 's/^/  - /'

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Summary:"
echo "  ✓ Applications: Use .kit files, go to source/apps/"
echo "  ✓ Extensions: Use extension.toml, go to source/extensions/"
echo "  ✓ Microservices: Use .kit files, go to source/apps/ (like apps but with services/)"

