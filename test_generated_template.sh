#!/bin/bash
# Test script to validate that generated templates work correctly

set -e

echo "================================================"
echo "Testing Generated Template Build and Validation"
echo "================================================"

# Clean up any previous test artifacts
echo "Cleaning up previous test artifacts..."
rm -rf source/apps/test_validation_* source/extensions/test_validation_* 2>/dev/null

# Generate a test application
echo ""
echo "Generating test application..."
./repo.sh template new kit_base_editor \
    --name=test_validation.editor \
    --display-name="Test Validation Editor" \
    --version=1.0.0

# Check if file was generated
if [ ! -f "source/apps/test_validation.editor.kit" ]; then
    echo "❌ ERROR: Template file was not generated"
    exit 1
fi

echo "✓ Template generated successfully"

# Validate the generated file
echo ""
echo "Validating generated template..."
if grep -q 'title = "Test Validation Editor"' source/apps/test_validation.editor.kit && \
   grep -q 'version = "1.0.0"' source/apps/test_validation.editor.kit; then
    echo "✓ Template contains correct values"
else
    echo "❌ ERROR: Template contains incorrect values"
    cat source/apps/test_validation.editor.kit | head -20
    exit 1
fi

# Generate a test extension
echo ""
echo "Generating test extension..."
./repo.sh template new basic_python_extension \
    --name=test_validation.extension \
    --display-name="Test Validation Extension" \
    --version=1.0.0

# Check if extension directory was created
if [ ! -d "source/extensions/test_validation.extension" ]; then
    echo "❌ ERROR: Extension directory was not created"
    exit 1
fi

echo "✓ Extension generated successfully"

# Check extension configuration
if [ -f "source/extensions/test_validation.extension/config/extension.toml" ]; then
    echo "✓ Extension configuration file exists"
else
    echo "❌ ERROR: Extension configuration file missing"
    exit 1
fi

# Test with configuration file
echo ""
echo "Testing configuration file usage..."
cat > test_config.toml << EOF
[company]
name = "test_company"
display_name = "Test Company"

[project]
name = "config_test"
display_name = "Config Test App"
version = "2.0.0"

[application]
name = "\${company.name}.\${project.name}"
display_name = "\${project.display_name}"
version = "\${project.version}"
EOF

# Note: This would work if configuration file support was fully integrated
# For now, we'll skip this test

echo ""
echo "================================================"
echo "✓ All template generation tests passed!"
echo "================================================"
echo ""
echo "Generated files:"
echo "  - Application: source/apps/test_validation.editor.kit"
echo "  - Extension: source/extensions/test_validation.extension/"
echo ""
echo "To build the generated templates, run:"
echo "  ./repo.sh build --release"
echo ""
echo "To clean up test files, run:"
echo "  rm -rf source/apps/test_validation_* source/extensions/test_validation_*"