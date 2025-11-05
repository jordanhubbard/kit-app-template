#!/bin/bash

echo "=== Comparing Official Upstream vs Your Complete Repo ==="
echo ""

OFFICIAL="/home/jkh/Src/upstream-kit-app-template"
YOURS="/home/jkh/Src/kit-app-template"

echo "Official upstream: $OFFICIAL"
echo "Your complete repo: $YOURS"
echo ""

echo "=== Files ONLY in Official Upstream (not in your repo) ==="
cd "$OFFICIAL"
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.toml" -o -name "*.json" \) \
    | grep -v "\.git\|_build\|__pycache__\|node_modules" \
    | while read file; do
        if [ ! -f "$YOURS/$file" ]; then
            echo "$file"
        fi
    done | head -50

echo ""
echo "=== Files ONLY in Your Repo (not in official upstream) ==="
cd "$YOURS"
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.toml" -o -name "*.json" \) \
    | grep -v "\.git\|_build\|__pycache__\|node_modules\|_repo\|_compiler\|_testoutput" \
    | while read file; do
        if [ ! -f "$OFFICIAL/$file" ]; then
            echo "$file"
        fi
    done | head -50

echo ""
echo "=== Files DIFFERENT between repos ==="
cd "$YOURS"
find . -type f \( -name "*.py" -o -name "*.md" \) \
    | grep -v "\.git\|_build\|__pycache__\|node_modules\|_repo\|_compiler\|_testoutput" \
    | while read file; do
        if [ -f "$OFFICIAL/$file" ]; then
            if ! diff -q "$file" "$OFFICIAL/$file" > /dev/null 2>&1; then
                echo "$file"
            fi
        fi
    done | head -50

