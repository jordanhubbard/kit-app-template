#!/bin/bash
# Test all application templates to see which ones work

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
declare -A RESULTS

# Application templates to test
TEMPLATES=(
    "omni.usd_viewer"
    "omni.usd_explorer"
    "omni.usd_composer"
    "kit.base_editor"
)

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Testing Application Templates                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

for template in "${TEMPLATES[@]}"; do
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Testing template: ${template}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Generate test project name
    TEST_NAME="test_$(echo $template | tr '.' '_')_$$"

    # Step 1: Create from template
    echo -e "${YELLOW}[1/4] Creating project from template...${NC}"
    if ./repo.sh template new --template "$template" --dest-name "$TEST_NAME" --no-confirm 2>&1 | grep -q "successfully"; then
        echo -e "${GREEN}✓ Project created${NC}"
    else
        echo -e "${RED}✗ Failed to create project${NC}"
        RESULTS["$template"]="CREATE_FAILED"
        continue
    fi

    # Step 2: Build
    echo -e "${YELLOW}[2/4] Building project...${NC}"
    if ./repo.sh build --name "${TEST_NAME}.kit" 2>&1 | tail -20; then
        if [ -f "_build/linux-x86_64/release/${TEST_NAME}.kit.sh" ]; then
            echo -e "${GREEN}✓ Build successful${NC}"
        else
            echo -e "${RED}✗ Build completed but launcher not found${NC}"
            RESULTS["$template"]="BUILD_NO_LAUNCHER"
            continue
        fi
    else
        echo -e "${RED}✗ Build failed${NC}"
        RESULTS["$template"]="BUILD_FAILED"
        continue
    fi

    # Step 3: Quick launch test (no Xpra, just check if it starts)
    echo -e "${YELLOW}[3/4] Testing launch (no display)...${NC}"
    timeout 5 ./_build/linux-x86_64/release/${TEST_NAME}.kit.sh --no-window --/app/quitAfter=1 2>&1 | head -20 &
    LAUNCH_PID=$!
    sleep 3

    if ps -p $LAUNCH_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Launch test passed (app started)${NC}"
        kill $LAUNCH_PID 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠ Launch test: app exited quickly (might be normal)${NC}"
    fi

    # Step 4: Xpra launch test
    echo -e "${YELLOW}[4/4] Testing Xpra launch...${NC}"
    DISPLAY=:100 timeout 10 ./_build/linux-x86_64/release/${TEST_NAME}.kit.sh 2>&1 | head -30 &
    XPRA_PID=$!
    sleep 5

    if ps -p $XPRA_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Xpra launch successful (app running)${NC}"
        # Check if window appeared
        if DISPLAY=:100 xdotool search --class --onlyvisible "." 2>/dev/null | grep -q .; then
            echo -e "${GREEN}✓✓ Window visible on Xpra display!${NC}"
            RESULTS["$template"]="SUCCESS_WITH_WINDOW"
        else
            echo -e "${YELLOW}⚠ App running but no window visible yet${NC}"
            RESULTS["$template"]="SUCCESS_NO_WINDOW"
        fi
        kill $XPRA_PID 2>/dev/null || true
    else
        # Check exit code
        wait $XPRA_PID 2>/dev/null
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 124 ]; then
            echo -e "${YELLOW}⚠ Launch timeout (app might be slow to start)${NC}"
            RESULTS["$template"]="TIMEOUT"
        else
            echo -e "${RED}✗ Xpra launch failed (exit code: $EXIT_CODE)${NC}"
            RESULTS["$template"]="LAUNCH_FAILED"
        fi
    fi

    echo ""
done

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Test Results Summary                                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

for template in "${TEMPLATES[@]}"; do
    result="${RESULTS[$template]}"
    case "$result" in
        "SUCCESS_WITH_WINDOW")
            echo -e "${GREEN}✓✓${NC} $template: ${GREEN}SUCCESS - Window visible on Xpra${NC}"
            ;;
        "SUCCESS_NO_WINDOW")
            echo -e "${GREEN}✓${NC}  $template: ${GREEN}SUCCESS - App running, no window yet${NC}"
            ;;
        "TIMEOUT")
            echo -e "${YELLOW}⚠${NC}  $template: ${YELLOW}TIMEOUT - App may be slow${NC}"
            ;;
        "LAUNCH_FAILED")
            echo -e "${RED}✗${NC}  $template: ${RED}FAILED - Launch error${NC}"
            ;;
        "BUILD_FAILED")
            echo -e "${RED}✗${NC}  $template: ${RED}FAILED - Build error${NC}"
            ;;
        "BUILD_NO_LAUNCHER")
            echo -e "${RED}✗${NC}  $template: ${RED}FAILED - No launcher created${NC}"
            ;;
        "CREATE_FAILED")
            echo -e "${RED}✗${NC}  $template: ${RED}FAILED - Project creation error${NC}"
            ;;
        *)
            echo -e "${YELLOW}?${NC}  $template: ${YELLOW}UNKNOWN${NC}"
            ;;
    esac
done

echo ""
echo -e "${BLUE}Cleaning up test projects...${NC}"
# Note: We're keeping them for now in case you want to inspect them
echo -e "${YELLOW}Test projects left in source/apps/ for inspection${NC}"
echo ""

