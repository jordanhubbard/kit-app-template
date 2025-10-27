# Clever Summit

## Overview

This is a standalone application project generated from the 'kit_base_editor' template.

The Kit Base Editor provides a minimal starting point for developers aiming to create
interactive 3D applications within the NVIDIA Omniverse ecosystem. This template
simplifies the process of crafting applications capable of loading, manipulating,
and rendering OpenUSD content via a graphical user interface.


## Project Information

- **Name**: clever_summit_1
- **Version**: 1.0.0
- **Template**: kit_base_editor
- **Type**: Application

## Prerequisites

- **Operating System**: Windows 10/11 or Linux (Ubuntu 22.04 or newer)
- **GPU**: NVIDIA RTX capable GPU (RTX 3070 or better recommended)
- **Driver**: Minimum 537.58
- **Git**: For version control
- **Git LFS**: For managing large files

## Building the Project

### Linux
```bash
./repo.sh build
```

### Windows
```powershell
.\repo.bat build
```

## Running the Project

### Linux
```bash
./repo.sh launch
```

### Windows
```powershell
.\repo.bat launch
```

## Available Commands

- `build` - Build the project
- `launch` - Launch the application
- `test` - Run tests
- `package` - Package for distribution
- `clean` - Clean build artifacts

## Project Structure

```
.
├── source/              # Source code
│   ├── apps/           # Application definitions
│   └── extensions/     # Extension modules
├── tools/              # Build and development tools
├── _build/             # Build output (generated)
├── _compiler/          # Compiler artifacts (generated)
└── _repo/              # Repository cache (generated)
```

## Development

This project includes all necessary build tools and dependencies to work as a standalone repository. You can:

1. Initialize a new git repository: `git init`
2. Add your changes: `git add .`
3. Commit: `git commit -m "Initial commit"`
4. Push to your remote repository

## Documentation

For more information about the Omniverse Kit SDK and development practices, visit:
- [Omniverse Kit SDK Manual](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/index.html)
- [Kit App Template Documentation](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html)

## License

This project is based on the NVIDIA Omniverse Kit SDK and is subject to the NVIDIA Software License Agreement and Product-Specific Terms for NVIDIA Omniverse.

---

Generated with the Kit App Template system
