# Standalone Projects Guide

Create self-contained Kit applications that can be built and run independently of the kit-app-template repository.

---

## What is a Standalone Project?

A standalone project is a complete, self-contained application generated from a template that includes:

✅ All source code
✅ All build tools (packman, repoman)
✅ All configuration files
✅ Build scripts (repo.sh, repo.bat)
✅ Complete documentation

**Key benefit**: No dependency on the original kit-app-template repository. Can be moved, shared, or distributed as a single directory.

---

## Quick Start

### Create a Standalone Project

```bash
./repo.sh template new kit_base_editor \
  --name my.app \
  --standalone \
  --accept-license
```

This creates a standalone project in `./my.app/`

### Build and Run

```bash
cd my.app
./repo.sh build
./repo.sh launch --name my.app.kit
```

---

## Usage Examples

### Example 1: Create in Current Directory

```bash
# Creates ./my_editor/ as standalone project
./repo.sh template new kit_base_editor \
  --name my_editor \
  --standalone \
  --accept-license
```

### Example 2: Create in Specific Location

```bash
# Creates ~/projects/my-app/ as standalone project
./repo.sh template new omni_usd_viewer \
  --name my.viewer \
  --output-dir ~/projects/my-app \
  --standalone \
  --accept-license
```

### Example 3: Create Microservice

```bash
# Creates standalone microservice
./repo.sh template new kit_service \
  --name my.service \
  --standalone \
  --accept-license
```

---

## Standalone vs Repository Mode

| Feature | Repository Mode | Standalone Mode |
|---------|----------------|-----------------|
| **Location** | `source/apps/` within repo | Any directory |
| **Build Tools** | Shared from repository | Included in project |
| **Dependencies** | Repository-level | Project-level |
| **Distribution** | Requires repository | Self-contained zip/tar |
| **Updates** | Pull from repo | Standalone updates |
| **Team Sharing** | Share repository | Share project directory |

---

## Project Structure

A standalone project has this structure:

```
my.app/                           # Project root (can be anywhere)
├── repo.sh / repo.bat            # Build scripts
├── repo.toml                     # Configuration
├── premake5.lua                  # Build configuration
├── README.md                     # Usage instructions
├── requirements.txt              # Python dependencies
│
├── tools/                        # Build tools (self-contained)
│   ├── packman/                  # Dependency manager
│   │   ├── packman               # Packman executable
│   │   ├── python.sh             # Python bootstrap
│   │   └── ...
│   └── repoman/                  # Build system
│       ├── repoman.py            # Build orchestrator
│       ├── launch.py             # Launcher
│       └── ...
│
└── source/                       # Application source
    └── apps/my.app/              # Your application
        ├── my.app.kit            # Main config
        ├── README.md             # App docs
        └── ...
```

---

## Working with Standalone Projects

### Building

```bash
cd my-standalone-app

# Build release version
./repo.sh build

# Build debug version
./repo.sh build --config debug

# Clean build
./repo.sh build --clean
```

### Running

```bash
# Launch application
./repo.sh launch --name my.app.kit

# Launch with arguments
./repo.sh launch --name my.app.kit --verbose
```

### Packaging

```bash
# Create distributable package
./repo.sh package
```

---

## Distribution

### Sharing Standalone Projects

Standalone projects can be easily shared:

#### Option 1: Archive

```bash
# Create archive
tar -czf my-app.tar.gz my-standalone-app/

# Or zip
zip -r my-app.zip my-standalone-app/
```

#### Option 2: Git Repository

```bash
cd my-standalone-app
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

#### Option 3: Direct Copy

Simply copy the entire directory:

```bash
cp -r my-standalone-app /path/to/destination/
```

---

## Development Workflow

### 1. Create Standalone Project

```bash
./repo.sh template new kit_base_editor \
  --name my.project \
  --standalone \
  --accept-license
```

### 2. Develop

```bash
cd my.project

# Edit source files in source/apps/my.project/

# Build and test
./repo.sh build
./repo.sh launch --name my.project.kit
```

### 3. Share

```bash
# Archive entire project
cd ..
tar -czf my.project.tar.gz my.project/

# Recipients can extract and use immediately
tar -xzf my.project.tar.gz
cd my.project
./repo.sh build
```

---

## Advanced Topics

### Custom Output Directory

```bash
# Absolute path
./repo.sh template new kit_base_editor \
  --name my.app \
  --output-dir /home/user/projects/my-app \
  --standalone

# Relative path
./repo.sh template new kit_base_editor \
  --name my.app \
  --output-dir ../standalone-apps/my-app \
  --standalone
```

### Multiple Standalone Projects

You can create multiple standalone projects from the same repository:

```bash
# Create editor
./repo.sh template new kit_base_editor \
  --name editor \
  --output-dir ~/apps/editor \
  --standalone

# Create viewer
./repo.sh template new omni_usd_viewer \
  --name viewer \
  --output-dir ~/apps/viewer \
  --standalone

# Create service
./repo.sh template new kit_service \
  --name service \
  --output-dir ~/apps/service \
  --standalone
```

Each is completely independent.

### Extensions in Standalone Projects

Extensions work the same way in standalone projects:

```bash
cd my-standalone-app

# Create extension within standalone project
./repo.sh template new basic_python_extension \
  --name my.extension
```

---

## Troubleshooting

### Build Fails

**Problem**: Build fails with missing dependencies

**Solution**:
```bash
# Clean build directory
rm -rf _build/
./repo.sh build
```

Packman will download all dependencies automatically.

---

### Launch Fails

**Problem**: Application fails to launch

**Solution**:
1. Verify build succeeded: `./repo.sh build`
2. Check `.kit` file exists in build output
3. Try with full path:
   ```bash
   ./repo.sh launch --name $(pwd)/_build/linux-x86_64/release/apps/my.app/my.app.kit
   ```

---

### Directory Already Exists

**Problem**: `--standalone` warns directory exists

**Behavior**: Template is created in `source/apps/` but standalone generation is skipped

**Solution**:
```bash
# Remove existing directory
rm -rf target-directory

# Or use different output directory
./repo.sh template new ... --output-dir different-directory --standalone
```

---

### Moving Standalone Project

**Problem**: Does moving break the project?

**Answer**: No! Standalone projects work from any location:

```bash
# Create
./repo.sh template new kit_base_editor --name my.app --standalone

# Move anywhere
mv my.app ~/projects/

# Still works
cd ~/projects/my.app
./repo.sh build
```

---

## Best Practices

### ✅ DO

- ✅ Use `--standalone` for projects you'll share
- ✅ Use `--standalone` for customer deliverables
- ✅ Use `--standalone` for isolated development
- ✅ Archive standalone projects for distribution
- ✅ Version control standalone projects with Git
- ✅ Test standalone projects after moving

### ❌ DON'T

- ❌ Don't modify `tools/` directory manually
- ❌ Don't expect automatic updates from repository
- ❌ Don't share repository mode projects (missing tools)
- ❌ Don't assume paths are absolute

---

## FAQ

### Q: Can I update a standalone project from the repository?

**A**: No. Standalone projects are independent snapshots. To get updates:
1. Create a new standalone project from the updated template
2. Manually merge your changes

### Q: Can I convert a repository project to standalone?

**A**: Yes! Use `--standalone` with an existing app name:
```bash
./repo.sh template new kit_base_editor \
  --name existing_app_name \
  --output-dir ~/standalone-version \
  --standalone
```

### Q: How large are standalone projects?

**A**:
- Before build: ~15-20 MB (tools + source)
- After build: ~1-2 GB (includes Kit SDK)

### Q: Do standalone projects support all templates?

**A**: Yes! All templates (applications, extensions, microservices) work in standalone mode.

### Q: Can I create extensions in standalone projects?

**A**: Yes! The standalone project includes all template tools:
```bash
cd my-standalone-app
./repo.sh template new basic_python_extension --name my.ext
```

### Q: What's the difference between `--output-dir` and `--standalone`?

**A**:
- `--output-dir` alone: Creates template in specified directory (still needs repository)
- `--standalone` alone: Creates standalone project in `./app_name/`
- Both together: Creates standalone project in specified directory

---

## Examples by Use Case

### For Solo Developers

```bash
# Create standalone project for your app
./repo.sh template new kit_base_editor \
  --name my.personal.app \
  --standalone
```

### For Teams

```bash
# Create standalone project in shared location
./repo.sh template new omni_usd_viewer \
  --name team.viewer \
  --output-dir /shared/projects/viewer \
  --standalone

# Team members can build directly
cd /shared/projects/viewer
./repo.sh build
```

### For Customers

```bash
# Create deliverable
./repo.sh template new kit_base_editor \
  --name customer.app \
  --standalone

# Archive for delivery
tar -czf customer-app-v1.0.tar.gz customer.app/

# Customer extracts and builds
tar -xzf customer-app-v1.0.tar.gz
cd customer.app
./repo.sh build
```

### For Experimentation

```bash
# Create throwaway standalone project
./repo.sh template new kit_base_editor \
  --name experiment \
  --output-dir /tmp/experiment \
  --standalone

cd /tmp/experiment
# Experiment freely, delete when done
```

---

## Related Documentation

- [Template System Guide](templates/README.md)
- [Build System Guide](README.md#building)
- [CLI Reference](CLI_FEATURES.md)
- [Project Structure](PLAN.md)

---

## Summary

**Standalone projects** enable true independence:

✅ Self-contained and portable
✅ Include all build tools
✅ No repository dependencies
✅ Easy to share and distribute
✅ Work from any location

**Perfect for**:
- Customer deliverables
- Team projects
- Isolated development
- Distribution/sharing

**Command**:
```bash
./repo.sh template new <template> --name <name> --standalone
```

---

**Generated**: kit-app-template Phase 5
**Version**: 1.0
**Status**: Production Ready
