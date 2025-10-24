# Migration Guide: Per-Application Dependencies

**Audience**: Existing kit-app-template users  
**Goal**: Migrate existing apps to use per-app dependencies  
**Time**: 5-15 minutes per app

---

## Should You Migrate?

### Reasons to Migrate

✅ **Migrate if you**:
- Have multiple apps needing different Kit versions
- Experience dependency conflicts between apps
- Want to test experimental Kit builds per app
- Need strict dependency isolation
- Work in a multi-developer environment

### Reasons NOT to Migrate

❌ **Don't migrate if you**:
- Have a single app
- All apps use the same Kit version
- Disk space is very limited
- Apps are temporary/prototypes

---

## Migration Process

### Step 1: Understand Current Setup

**Before Migration**:
```
_build/linux-x86_64/release/
├── kit/                # Shared by ALL apps
└── apps/
    ├── app1/
    ├── app2/
    └── app3/
```

**After Migration**:
```
source/apps/app1/
├── _kit/               # App1's own Kit SDK
└── dependencies/
    └── kit-deps.toml

source/apps/app2/
├── _kit/               # App2's own Kit SDK  
└── dependencies/
    └── kit-deps.toml
```

---

### Step 2: Choose Migration Strategy

#### Option A: Migrate All Apps (Recommended)

Best for repositories with multiple apps that may diverge in dependencies.

```bash
# Migrate all apps at once
for app in source/apps/*; do
    ./tools/migrate_to_per_app_deps.sh $(basename $app)
done
```

#### Option B: Migrate Selectively

Best when only some apps need isolation.

```bash
# Migrate only apps that need it
./tools/migrate_to_per_app_deps.sh app1
./tools/migrate_to_per_app_deps.sh app3
# app2 stays on global deps
```

#### Option C: Manual Migration

Best for understanding the process or custom setups.

---

### Step 3: Manual Migration (Detailed)

For app `my_app`:

#### 3.1: Create Dependencies Configuration

```bash
# Create dependencies directory
mkdir -p source/apps/my_app/dependencies

# Create kit-deps.toml
cat > source/apps/my_app/dependencies/kit-deps.toml << 'EOF'
[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"

[dependencies]
EOF
```

#### 3.2: Determine Current Kit Version

```bash
# Find current Kit version
grep -r "kit-sdk" tools/deps/ | head -1

# Or check _build directory
ls -la _build/linux-x86_64/release/kit/
```

Update `kit-deps.toml` with the version you found.

#### 3.3: Rebuild App

```bash
# Clean rebuild to fetch per-app Kit
./repo.sh build --app my_app --clean
```

This will:
- Download Kit SDK to `source/apps/my_app/_kit/kit/`
- Set up app-specific dependencies
- Create per-app packman cache

#### 3.4: Verify Migration

```bash
# Check structure
ls -la source/apps/my_app/_kit/

# Should see:
# _kit/kit/           - Kit SDK
# _kit/cache/         - Packman cache

# Launch to test
./repo.sh launch my_app

# Should see:
# "Using per-app Kit SDK from: source/apps/my_app/_kit"
```

---

### Step 4: Cleanup (Optional)

After migrating all apps, you can remove global Kit SDK:

```bash
# WARNING: Only do this after ALL apps are migrated!

# Remove global Kit SDK
rm -rf _build/linux-x86_64/release/kit/

# Rebuild to verify all apps use per-app Kit
./repo.sh build
```

---

## Migration Checklist

Use this checklist for each app:

- [ ] Create `source/apps/<app>/dependencies/` directory
- [ ] Create `kit-deps.toml` with Kit version
- [ ] Verify TOML syntax is valid
- [ ] Clean rebuild: `./repo.sh build --app <app> --clean`
- [ ] Verify `_kit/` directory exists
- [ ] Test launch: `./repo.sh launch <app>`
- [ ] Verify "Using per-app Kit SDK" message appears
- [ ] Test app functionality
- [ ] Update app README if needed

---

## Migration Scripts

### Automated Migration Script

Create `tools/migrate_to_per_app_deps.sh`:

```bash
#!/bin/bash
# Migrate app to per-app dependencies

APP_NAME=$1
APP_PATH="source/apps/$APP_NAME"

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app_name>"
    exit 1
fi

if [ ! -d "$APP_PATH" ]; then
    echo "Error: App not found: $APP_PATH"
    exit 1
fi

echo "Migrating $APP_NAME to per-app dependencies..."

# Create dependencies directory
mkdir -p "$APP_PATH/dependencies"

# Create kit-deps.toml if it doesn't exist
if [ ! -f "$APP_PATH/dependencies/kit-deps.toml" ]; then
    cat > "$APP_PATH/dependencies/kit-deps.toml" << 'EOF'
[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"

[dependencies]
EOF
    echo "✓ Created dependencies/kit-deps.toml"
else
    echo "✓ Dependencies config already exists"
fi

# Rebuild app
echo "Rebuilding app with per-app dependencies..."
./repo.sh build --app "$APP_NAME"

if [ $? -eq 0 ]; then
    echo "✓ Migration complete for $APP_NAME"
    echo ""
    echo "To verify:"
    echo "  ./repo.sh launch $APP_NAME"
    echo ""
    echo "You should see:"
    echo "  'Using per-app Kit SDK from: $APP_PATH/_kit'"
else
    echo "✗ Build failed. Check errors above."
    exit 1
fi
```

Make it executable:
```bash
chmod +x tools/migrate_to_per_app_deps.sh
```

---

## Rollback

If migration causes issues, you can rollback:

### Rollback Single App

```bash
# Remove per-app deps config
rm -rf source/apps/my_app/dependencies/

# Remove per-app Kit SDK
rm -rf source/apps/my_app/_kit/

# Rebuild with global Kit
./repo.sh build --app my_app
```

### Rollback All Apps

```bash
# Remove all per-app deps
find source/apps -name "dependencies" -type d -exec rm -rf {} +
find source/apps -name "_kit" -type d -exec rm -rf {} +

# Rebuild all apps with global Kit
./repo.sh build
```

---

## Common Migration Issues

### Issue 1: Build Fails After Migration

**Symptoms**:
```
Error: Kit SDK not found
Failed to download dependencies
```

**Solutions**:
1. Check `kit-deps.toml` syntax
2. Verify Kit version is valid
3. Check internet connection
4. Try clean rebuild: `./repo.sh build --app <app> --clean`

### Issue 2: App Uses Global Kit After Migration

**Symptoms**:
- No "Using per-app Kit SDK" message
- `_kit/` directory missing

**Solutions**:
1. Verify `dependencies/kit-deps.toml` exists
2. Check TOML file is not empty
3. Rebuild: `./repo.sh build --app <app>`
4. Check for typos in directory/file names

### Issue 3: Disk Space Warning

**Symptoms**:
```
Warning: Low disk space
Each app will download ~1-2 GB
```

**Solutions**:
1. Use `strategy = "shared"` in `kit-deps.toml`
2. Migrate only critical apps
3. Free up disk space
4. Use external storage for `_kit/` directories

### Issue 4: Existing Build Artifacts Conflict

**Symptoms**:
- Mixed behavior between global and per-app Kit
- Unexpected Kit version being used

**Solutions**:
```bash
# Clean all build artifacts
./repo.sh clean

# Clean rebuild with per-app deps
./repo.sh build --app <app> --clean
```

---

## Testing After Migration

### Test Plan

1. **Build Test**
   ```bash
   ./repo.sh build --app <app>
   # Should succeed without errors
   ```

2. **Launch Test**
   ```bash
   ./repo.sh launch <app>
   # Should see "Using per-app Kit SDK from: ..."
   ```

3. **Functionality Test**
   - Test all major app features
   - Verify extensions load correctly
   - Check for runtime errors

4. **Multiple App Test** (if applicable)
   ```bash
   # Launch multiple apps simultaneously
   ./repo.sh launch app1 &
   ./repo.sh launch app2 &
   # Both should work independently
   ```

---

## Best Practices Post-Migration

### 1. Document Dependencies

Add to app's README:

```markdown
## Dependencies

This app uses per-app dependencies.

Kit SDK Version: 106.0
Cache Strategy: isolated

To rebuild: `./repo.sh build --app my_app`
```

### 2. Version Control

Commit the configuration:

```bash
git add source/apps/*/dependencies/
git commit -m "Migrate apps to per-app dependencies"
```

**Note**: Do NOT commit `_kit/` directories (already in `.gitignore`).

### 3. CI/CD Updates

Update build scripts:

```yaml
# .github/workflows/build.yml
- name: Build apps
  run: |
    # Apps will automatically use per-app deps
    ./repo.sh build
```

### 4. Team Communication

Inform team members:

```markdown
## Migration Notice

Apps now use per-app dependencies.

What this means:
- Each app has its own Kit SDK
- First build will download dependencies (~1-2 GB)
- Apps can use different Kit versions
- Existing commands work unchanged

No action required - just rebuild:
`./repo.sh build`
```

---

## Advanced: Gradual Migration

For large repositories, migrate gradually:

### Week 1: Pilot Apps
```bash
# Migrate 1-2 non-critical apps
./tools/migrate_to_per_app_deps.sh test_app
# Monitor for issues
```

### Week 2: Core Apps
```bash
# Migrate important production apps
./tools/migrate_to_per_app_deps.sh main_app
./tools/migrate_to_per_app_deps.sh dashboard_app
```

### Week 3: Remaining Apps
```bash
# Migrate all remaining apps
for app in source/apps/*; do
    if [ ! -d "$app/dependencies" ]; then
        ./tools/migrate_to_per_app_deps.sh $(basename $app)
    fi
done
```

### Week 4: Cleanup
```bash
# Remove global Kit SDK
rm -rf _build/*/kit/
# Verify all apps work
./repo.sh build && ./repo.sh test
```

---

## FAQ

**Q: Will this break my existing builds?**  
A: No, apps without `dependencies/kit-deps.toml` continue using global Kit.

**Q: Can I migrate incrementally?**  
A: Yes! Apps can mix per-app and global dependencies.

**Q: How long does migration take?**  
A: 5-15 minutes per app (mostly download time).

**Q: Can I revert if something breaks?**  
A: Yes, delete `dependencies/` and `_kit/` directories and rebuild.

**Q: Do I need to modify my code?**  
A: No code changes needed. Only configuration changes.

**Q: What about CI/CD pipelines?**  
A: No changes needed. Apps auto-detect per-app deps during build.

---

## Support

If you encounter issues during migration:

1. Check [PER_APP_DEPENDENCIES.md](./PER_APP_DEPENDENCIES.md) troubleshooting
2. Run tests: `make test-compatibility`
3. File an issue with:
   - App name
   - Migration steps taken
   - Error messages
   - `kit-deps.toml` content

---

**Ready to migrate?** Follow Step 3 above or use the automated script!

