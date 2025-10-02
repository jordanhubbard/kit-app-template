# Omniverse Kit App Template

<p align="center">
  <img src="readme-assets/kit_app_template_banner.png" width=100% />
</p>

## :memo: Feature Branch Information
**This repository is based on a Feature Branch of the Omniverse Kit SDK.** Feature Branches are regularly updated and best suited for testing and prototyping.
For stable, production-oriented development, please use the [Production Branch of the Kit SDK on NVIDIA GPU Cloud (NGC)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/collections/omniverse_enterprise_25h1).

[Omniverse Release Information](https://docs.omniverse.nvidia.com/dev-overview/latest/omniverse-releases.html#)


## Overview

Welcome to `kit-app-template`, a toolkit designed for developers interested in GPU-accelerated application development within the NVIDIA Omniverse ecosystem. This repository offers streamlined tools and templates to simplify creating high-performance, OpenUSD-based desktop or cloud streaming applications using the Omniverse Kit SDK.

### About Omniverse Kit SDK

The Omniverse Kit SDK enables developers to build immersive 3D applications. Key features include:
- **Language Support:** Develop with either Python or C++, offering flexibility for various developer preferences.
- **OpenUSD Foundation:** Utilize the robust Open Universal Scene Description (OpenUSD) for creating, manipulating, and rendering rich 3D content.
- **GPU Acceleration:** Leverage GPU-accelerated capabilities for high-fidelity visualization and simulation.
- **Extensibility:** Create specialized extensions that provide dynamic user interfaces, integrate with various systems, and offer direct control over OpenUSD data, making the Omniverse Kit SDK versatile for numerous applications.

### Applications and Use Cases

The `kit-app-template` repository enables developers to create cross-platform applications (Windows and Linux) optimized for desktop use and cloud streaming. Potential use cases include designing and simulating expansive virtual environments, producing high-quality synthetic data for AI training, and building advanced tools for technical analysis and insights. Whether you're crafting engaging virtual worlds, developing comprehensive analysis tools, or creating simulations, this repository, along with the Kit SDK, provides the foundational components required to begin development.

### A Deeper Understanding

The `kit-app-template` repository is designed to abstract complexity, jumpstarting your development with pre-configured templates, tools, and essential boilerplate. For those seeking a deeper understanding of the application and extension creation process, we have provided the following resources:

#### Companion Tutorial

**[Explore the Kit SDK Companion Tutorial](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html)**: This tutorial offers detailed insights into the underlying structure and mechanisms, providing a thorough grasp of both the Kit SDK and the development process.

### New Developers

For a beginner-friendly introduction to application development using the Omniverse Kit SDK, see the NVIDIA DLI course:

#### Beginner Tutorial

**[Developing an Omniverse Kit-Based Application](https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-OV-11+V1)**: This course offers an accessible introduction to application development (account and login required).

These resources empower developers at all experience levels to fully utilize the `kit-app-template` repository and the Omniverse Kit SDK.

## Table of Contents
- [Overview](#overview)
- [Prerequisites and Environment Setup](#prerequisites-and-environment-setup)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Kit Playground - Visual Development Environment](#kit-playground---visual-development-environment)
    - [Getting Started with Kit Playground](#getting-started-with-kit-playground)
    - [Features](#kit-playground-features)
    - [Workflow](#visual-development-workflow)
- [Enhanced Template System](#enhanced-template-system)
    - [Template Organization](#template-organization)
    - [Self-Documentation](#self-documentation)
    - [Template Composition](#template-composition)
    - [Standalone Projects](#standalone-projects)
- [Templates](#templates)
    - [Applications](#applications)
    - [Extensions](#extensions)
    - [Microservices](#microservices)
    - [Components](#components)
- [Tools](#tools)
- [License](#license)
- [Additional Resources](#additional-resources)
- [Contributing](#contributing)

## Prerequisites and Environment Setup

Ensure your system is set up with the following to work with Omniverse Applications and Extensions:

- **Operating System**: Windows 10/11 or Linux (Ubuntu 22.04 or newer)

- **GPU**: NVIDIA RTX capable GPU (RTX 3070 or Better recommended)

- **Driver**: Minimum and recommended - 537.58. Newer versions may work but are not equally validated.

- **Internet Access**: Required for downloading the Omniverse Kit SDK, extensions, and tools.

### Required Software Dependencies

- [**Git**](https://git-scm.com/downloads): For version control and repository management

- [**Git LFS**](https://git-lfs.com/): For managing large files within the repository

- **Python 3.8+**: Required for the template system and build tools.
  - **Required Python packages**: `toml` or `tomli` (for Python < 3.11) - **automatically installed on first run** of `repo.sh` or `repo.bat`, or via `make install-python-deps`

- **(Windows - C++ Only) Microsoft Visual Studio (2019 or 2022)**: You can install the latest version from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/). Ensure that the **Desktop development with C++** workload is selected.  [Additional information on Windows development configuration](readme-assets/additional-docs/windows_developer_configuration.md)

- **(Windows - C++ Only) Windows SDK**: Install this alongside MSVC. You can find it as part of the Visual Studio Installer. [Additional information on Windows development configuration](readme-assets/additional-docs/windows_developer_configuration.md)

- **(Linux) build-essentials**: A package that includes `make` and other essential tools for building applications.  For Ubuntu, install with `sudo apt-get install build-essential`

### Recommended Software

- [**(Linux) Docker**](https://docs.docker.com/engine/install/ubuntu/): For containerized development and deployment. **Ensure non-root users have Docker permissions.**

- [**(Linux) NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html): For GPU-accelerated containerized development and deployment. **Installation and Configuring Docker steps are required.**

- [**VSCode**](https://code.visualstudio.com/download) (or your preferred IDE): For code editing and development


## Repository Structure

| Directory Item   | Purpose                                                    |
|------------------|------------------------------------------------------------|
| .vscode          | VS Code configuration details and helper tasks             |
| readme-assets/   | Images and additional repository documentation             |
| templates/       | Enhanced data-driven template system with hierarchical organization |
| ├─ applications/ | Standalone runnable application templates                   |
| ├─ extensions/   | Reusable extension templates organized by language          |
| ├─ microservices/| Headless API service templates                             |
| ├─ components/   | Non-standalone building block templates                     |
| └─ template_registry.toml | Centralized template discovery, organization, and relationship config |
| tools/           | Tooling settings and repository specific (local) tools     |
| ├─ repoman/      | Repository management tools and OS-independent command dispatcher |
| .editorconfig    | [EditorConfig](https://editorconfig.org/) file.            |
| .gitattributes   | Git configuration.                                         |
| .gitignore       | Git configuration.                                         |
| LICENSE          | License for the repo.                                      |
| README.md        | Project information.                                       |
| premake5.lua     | Build configuration - such as what apps to build.          |
| repo.bat         | Windows repo tool entry point.                             |
| repo.sh          | Linux repo tool entry point.                               |
| repo.toml        | Top level configuration of repo tools.                     |
| repo_tools.toml  | Setup of local, repository specific tools                  |

## Quick Start

You can develop Kit applications using either the **Visual Kit Playground** (recommended for beginners) or the **Command Line Interface**. Choose the approach that best fits your workflow.

> **Architecture Note:** The CLI and Kit Playground are **independent systems**. The CLI is a monolithic application that works standalone without any web server or background services. Kit Playground is an optional browser-based UI that provides a visual development experience. You can use either or both, and they do not interfere with each other.

### Option 1: Visual Development with Kit Playground (Recommended)

Kit Playground provides a Swift Playgrounds-like visual environment where you can browse, edit, build, and run templates side-by-side without using the command line. **This is an optional tool** that launches a local web server for the visual interface.

**[Jump to Kit Playground Setup →](#kit-playground---visual-development-environment)**

### Option 2: Command Line Development

For developers who prefer traditional command-line workflows, follow the steps below. **The CLI tools work completely standalone** - no web server or additional services are required. For a more comprehensive explanation of functionality, reference the [Tutorial](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html).

### 1. Clone the Repository

Begin by cloning the `kit-app-template` to your local workspace:

#### 1a. Clone

```bash
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
```

#### 1b. Navigate to Cloned Directory

```bash
cd kit-app-template
```

### 2. Check and Install Dependencies (Optional)

> **NOTE:** Python dependencies (`toml` package) are automatically installed when you first run `./repo.sh` or `.\repo.bat` commands. This step is optional but recommended to verify your setup.

**Check all dependencies:**
```bash
make deps
```

**Install any missing dependencies:**
```bash
make install-deps
```

This will install:
- Python packages (toml/tomli) required for the template system
- Node.js and npm (if using Kit Playground)
- FUSE library (for running AppImages on Linux)

> **TIP:** If you only need to install Python dependencies, run `make install-python-deps`

### 3. Explore Available Templates

Before creating a new project, explore the available templates:

**List all templates:**
```bash
./repo.sh template list
```

**List templates by type:**
```bash
./repo.sh template list --type application
./repo.sh template list --type microservice
```

**View template documentation:**
```bash
./repo.sh template docs kit_base_editor
./repo.sh template docs kit_service
```

### 4. Create and Configure New Application From Template

Run the following command to create a new project:

**Linux:**
```bash
./repo.sh template new kit_base_editor --name my_company.my_editor --display-name "My Editor"
```

**Windows:**
```powershell
.\repo.bat template new kit_base_editor --name my_company.my_editor --display-name "My Editor"
```

> **NOTE:** If this is your first time running the `template new` tool, you'll be prompted to accept the Omniverse Licensing Terms.

Follow the prompt instructions:
- **? Select what you want to create with arrow keys ↑↓:** Application
- **? Select desired template with arrow keys ↑↓:** Kit Base Editor
- **? Enter name of application .kit file [name-spaced, lowercase, alphanumeric]:** [set application name]
- **? Enter application_display_name:** [set application display name]
- **? Enter version:** [set application version]

  Application [application name] created successfully in [path to project]/source/apps/[application name]

- **? Do you want to add application layers?** No

#### Explanation of Example Selections

• **`.kit` file name:** This file defines the application according to Kit SDK guidelines. The file name should be lowercase and alphanumeric to remain compatible with Kit’s conventions.

• **display name:** This is the application name users will see. It can be any descriptive text.

• **version:** The version number of the application. While you can use any format, semantic versioning (e.g., 0.1.0) is recommended for clarity and consistency.

• **application layers:** These optional layers add functionality for features such as streaming to web browsers. For this quick-start, we skip adding layers, but choosing "yes" would let you enable and configure streaming capabilities.

### 5. Build

Build your new application with the following command:


**Linux:**
```bash
./repo.sh build
```
**Windows:**
```powershell
.\repo.bat build
 ```

A successful build will result in the following message:

```text
BUILD (RELEASE) SUCCEEDED (Took XX.XX seconds)
```

 If you experience issues related to build, please see the [Usage and Troubleshooting](readme-assets/additional-docs/usage_and_troubleshooting.md) section for additional information.


### 6. Launch

Initiate your newly created application using:

**Linux:**
```bash
./repo.sh launch
```
**Windows:**
```powershell
.\repo.bat launch
```

**? Select with arrow keys which App would you like to launch:** [Select the created editor application]

![Kit Base Editor Image](readme-assets/kit_base_editor.png)


> **NOTE:** The initial startup may take 5 to 8 minutes as shaders compile for the first time. After initial shader compilation, startup time will reduce dramatically

## Kit Playground - Visual Development Environment

<p align="center">
  <img src="readme-assets/kit_playground_preview.png" width=100% />
</p>

Kit Playground is a **visual development environment** inspired by Swift Playgrounds that allows you to develop Omniverse Kit applications without touching the command line. It features a side-by-side editor and live preview, visual template gallery, and one-click build and deployment.

> **Important:** Kit Playground is an **optional tool** that provides a browser-based visual interface. It runs a local Flask web server on port 8081 for the UI. When you use `make playground`, it starts this web server which runs until you stop it (Ctrl+C). **The CLI commands (`./repo.sh`) work completely independently** and do not require the playground server to be running.

### Getting Started with Kit Playground

#### Prerequisites Check

First, check if you have all required dependencies:

```bash
make deps
```

If any dependencies are missing, install them automatically:

```bash
make install-deps
```

This will install:
- Python packages (toml/tomli) required for the template system
- Node.js and npm (required for Kit Playground UI)
- FUSE library (for running AppImages on Linux)

#### Installation

**All Platforms:**
```bash
# Install Kit Playground (first time only)
make playground-install

# Launch Kit Playground
make playground
```

**Alternative for Windows (without Make):**
```powershell
# If Make is not available, use the repo.bat wrapper:
.\repo.bat playground-install
.\repo.bat playground
```

The application will launch as a native desktop app using Electron.

#### First Run Setup

On first launch, Kit Playground will:
1. Start the Python backend server automatically
2. Index all available templates
3. Open the visual template gallery

### Kit Playground Features

#### 🎨 Visual Template Gallery
- **Browse** templates with thumbnail previews
- **Search** by name, category, or tags
- **Filter** by type (Application, Extension, Microservice)
- **Preview** template capabilities and connectors
- **One-click install** from the marketplace

#### ✏️ Side-by-Side Development
- **Split View**: Code editor on the left, live preview on the right
- **Monaco Editor**: Full VS Code editing experience
- **Syntax Highlighting**: Python, TypeScript, TOML support
- **IntelliSense**: Auto-completion and suggestions
- **Hot Reload**: Changes appear instantly in preview

#### 📱 Device Preview Modes
- Test on **Desktop** (1920×1080)
- Preview on **Tablet** (768×1024)
- Simulate **Phone** (375×812)
- Scale to **4K/TV** (3840×2160)
- **Zoom controls** from 25% to 200%

#### 🔗 Visual Connection System
- **Drag-and-drop** to connect templates
- **Automatic validation** of connector compatibility
- **Bi-directional** and **uni-directional** connections
- **Data source resolution** with guided prompts
- **Dependency visualization** graph

#### 🚀 Integrated Build & Run
- **One-click build** without leaving the playground
- **Run/Stop** controls in the toolbar
- **Console output** in bottom pane
- **Error highlighting** in the editor
- **Build status** indicators

#### 📦 Deployment Options
- **Export** as standalone project
- **Deploy** to cloud services
- **Package** for distribution
- **Copy** templates for customization

### Visual Development Workflow

1. **Launch Kit Playground**
   ```bash
   make playground
   ```

2. **Browse or Search Templates**
   - Click the gallery icon to browse visually
   - Use the marketplace to discover community templates
   - Search by functionality or use case

3. **Select a Template**
   - Click on any template to load it
   - View its code in the left pane
   - See connector specifications

4. **Edit and Preview Side-by-Side**
   - Code changes on the left
   - Live preview updates on the right
   - Test on different device sizes
   - Use fullscreen for detailed preview

5. **Connect Templates (Optional)**
   - Switch to connection view
   - Drag from output to input connectors
   - Resolve any data requirements
   - View the dependency graph

6. **Build and Run**
   - Click the build button (🔨)
   - Click run to start (▶️)
   - View console output below
   - Stop when done (⏹️)

7. **Deploy Your Application**
   - Click deploy button (☁️)
   - Choose standalone or cloud
   - Follow the deployment wizard
   - Get your packaged application

### Example: Creating a USD Viewer

1. **Open Kit Playground**
2. **Search** for "USD Viewer" in the gallery
3. **Click** to load the template
4. **Customize** the code (optional):
   ```python
   # Modify viewer settings
   viewport.set_camera_position(0, 0, 100)
   viewport.set_lighting_mode("cinematic")
   ```
5. **Click Run** to see your viewer
6. **Test** on different screen sizes
7. **Deploy** as a standalone application

### Kit Playground vs Command Line

| Feature | Kit Playground | Command Line |
|---------|---------------|--------------|
| **Visual Template Gallery** | ✅ Yes | ❌ Text list |
| **Side-by-Side Editing** | ✅ Yes | ❌ Separate windows |
| **Live Preview** | ✅ Built-in | ⚠️ Manual setup |
| **Device Testing** | ✅ One-click | ❌ Manual |
| **Marketplace** | ✅ Integrated | ⚠️ Manual download |
| **Deployment** | ✅ Wizard | ⚠️ Commands |
| **Learning Curve** | ✅ Beginner-friendly | ⚠️ Intermediate |

### Tips for Kit Playground

- **Keyboard Shortcuts**:
  - `Ctrl/Cmd + S`: Save project
  - `Ctrl/Cmd + B`: Build
  - `Ctrl/Cmd + R`: Run
  - `Ctrl/Cmd + .`: Stop
  - `F11`: Fullscreen preview

- **Best Practices**:
  - Start with a template close to your needs
  - Use the console to debug issues
  - Test on multiple device sizes
  - Save projects regularly
  - Use version control for team projects

## Creating Standalone Projects

For self-contained projects that don't require the main repository structure, use the `--output-dir` option:

**Create a standalone project:**
```bash
./repo.sh template new kit_service --name my_company.my_api --display-name "My API Service" --output-dir ./my-standalone-project
```

This creates a complete, self-contained project with:
- All necessary source code and configuration
- Complete build tooling (`repo.sh`, `premake5.lua`, etc.)
- Project-specific documentation
- Independent git repository ready for deployment

The generated project can be built and deployed independently:
```bash
cd ./my-standalone-project
./repo.sh build
./repo.sh launch
```

## Enhanced Template System

The Kit App Template features a comprehensive, data-driven template system with self-documentation, composition capabilities, and standalone project generation. The system has been completely redesigned to support template inheritance, configuration validation, and automated documentation.

### Template Organization

Templates are organized by type in a hierarchical structure managed by the `templates/template_registry.toml` configuration:

- **Applications** (`templates/applications/`) - Standalone runnable applications
- **Extensions** (`templates/extensions/`) - Reusable extension components organized by language
- **Microservices** (`templates/microservices/`) - Headless API services
- **Components** (`templates/components/`) - Non-standalone building blocks

Each template includes a comprehensive `template.toml` descriptor with metadata, documentation, variables, dependencies, and inheritance relationships.

### Self-Documentation

All templates are self-documenting with rich metadata and accessible via the command line:

**View specific template documentation:**
```bash
./repo.sh template docs <template_name>
```

**List all templates:**
```bash
./repo.sh template list
```

**List templates by type:**
```bash
./repo.sh template list --type application
./repo.sh template list --type extension
./repo.sh template list --type microservice
./repo.sh template list --type component
```

**Example documentation output:**
```bash
./repo.sh template docs kit_base_editor
# Kit Base Editor
# Type: Application
# Category: Editor
# Version: 1.0.0
#
# ## Overview
# The Kit Base Editor provides a minimal starting point for developers...
#
# ## Use Cases
# - High fidelity OpenUSD editing applications and tools
# - Interactive 3D content manipulation
#
# ## Getting Started
# 1. Run: ./repo.sh template new kit_base_editor --name my_company.my_app
```

### Template Composition

Templates support advanced inheritance and composition patterns managed by the template registry:

- **Inheritance**: Templates can extend base templates using the `extends` field in their `template.toml`
- **Dependencies**: Templates can require other templates as components via the registry's relationship system
- **Composition**: Complex applications can be built from multiple template components
- **Configuration Inheritance**: Variables and settings cascade through the template hierarchy
- **Registry Management**: The `template_registry.toml` file defines template relationships, dependencies, and categories

### Standalone Projects

Generate complete, self-contained projects in any directory:

```bash
./repo.sh template new <template_name> --output-dir /path/to/project
```

Standalone projects include:
- Complete source code and configuration
- All necessary build tools and scripts
- Self-contained `repo.sh` tooling
- Project-specific documentation

## Templates

`kit-app-template` features a comprehensive, data-driven template system with hierarchical organization, self-documentation, composition capabilities, and standalone project generation. The system supports template inheritance, configuration validation, and automated documentation generation.

Use `./repo.sh template list` to see all available templates organized by type, or `./repo.sh template docs <name>` for detailed auto-generated documentation about any template.

### Applications

Standalone runnable applications for various use cases:

- **Kit Base Editor** (`kit_base_editor`): Minimal template for loading, manipulating and rendering OpenUSD content from a graphical interface
- **USD Composer** (`omni_usd_composer`): Template for authoring complex OpenUSD scenes, such as configurators
- **USD Explorer** (`omni_usd_explorer`): Template for exploring and collaborating on large Open USD scenes
- **USD Viewer** (`omni_usd_viewer`): Viewport-only template optimized for streaming and remote interaction

### Extensions

Reusable extension components organized by programming language:

**Python Extensions:**
- **Basic Python** (`basic_python_extension`): Minimal definition of an Omniverse Python Extension
- **Python UI** (`basic_python_ui_extension`): Extension with easily extendable Python-based user interface

**C++ Extensions:**
- **Basic C++** (`basic_cpp_extension`): Minimal definition of an Omniverse C++ Extension
- **C++ w/ Python Bindings** (`basic_python_binding`): C++ Extension with Python interface via Pybind11

### Microservices

Headless API services for automation and cloud deployment:

- **Kit Service** (`kit_service`): Minimal definition of a headless Omniverse Kit SDK service with REST API endpoints

### Components

Non-standalone building blocks that enhance other templates:

**Setup Extensions:**
- Service setup extensions for configuring applications
- Composer, Explorer, and Viewer setup components

**Streaming Layers:**
- Default streaming configuration for web-based access
- NVCF and GDN streaming variants

   **Note for Windows C++ Developers**: C++ templates require `"platform:windows-x86_64".enabled` and `link_host_toolchain` within the `repo.toml` file be set to `true`. For additional C++ configuration information [see here](readme-assets/additional-docs/windows_developer_configuration.md).


## Application Streaming

The Omniverse Platform supports streaming Kit-based applications directly to a web browser. You can either manage your own deployment or use an NVIDIA-managed service:

### Self-Managed
- **Omniverse Kit App Streaming :** A reference implementation on GPU-enabled Kubernetes clusters for complete control over infrastructure and scalability.

### NVIDIA-Managed
- **NVIDIA Cloud Functions (NVCF):** Offloads hardware, streaming, and network complexities for secure, large scale deployments.

- **Graphics Delivery Network (GDN):** Streams high-fidelity 3D content worldwide with just a shared URL.

[Configuring and packaging streaming-ready Kit applications](readme-assets/additional-docs/kit_app_streaming_config.md)


## Tools

The Kit SDK includes a suite of tools to aid in the development, testing, and deployment of your projects. For a more detailed overview of available tooling, see the [Kit SDK Tooling Guide](readme-assets/additional-docs/kit_app_template_tooling_guide.md).

Here's a brief overview of some key tools:

- **Help (`./repo.sh -h` or `.\repo.bat -h`):** Provides a list of available tools and their descriptions.

### Template System

- **Cross-Platform Template Creation (`./repo.sh` or `.\repo.bat template new <name>`):** Generate new projects from templates with data-driven configuration, inheritance support, and variable interpolation. Uses OS-independent Python dispatcher for consistent behavior across Linux and Windows.
- **Enhanced Template Arguments (`./repo.sh template new <name> --name <app_name> --display-name "Display Name"`):** Non-interactive template creation with command-line arguments for automation and CI/CD pipelines.
- **Template Documentation (`./repo.sh template docs <name>`):** View comprehensive self-generated documentation including use cases, features, variables, and examples.
- **Template Discovery (`./repo.sh template list [--type=TYPE]`):** List all available templates with hierarchical organization, optionally filtered by type (application, extension, microservice, component).
- **Standalone Projects (`./repo.sh template new <name> --output-dir <path>`):** Create complete, self-contained projects with independent build tooling and git repository.
- **Template Registry Management:** Centralized template organization via `template_registry.toml` with relationships, dependencies, and categories.

### Development Tools

- **Build (`./repo.sh build` or `.\repo.bat build`):** Compiles your applications and extensions, preparing them for launch.

- **Launch (`./repo.sh launch` or `.\repo.bat launch`):** Starts your compiled application or extension.

- **Testing (`./repo.sh test` or `.\repo.bat test`):** Facilitates the execution of test suites for your extensions, ensuring code quality and functionality. Enhanced test framework support added.

- **Packaging (`./repo.sh package` or `.\repo.bat package`):** Aids in packaging your application for distribution, making it easier to share or deploy in cloud environments.

## Governing Terms
The software and materials are governed by the [NVIDIA Software License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement/) and the [Product-Specific Terms for NVIDIA Omniverse](https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-omniverse/).

## Data Collection
The Omniverse Kit SDK collects anonymous usage data to help improve software performance and aid in diagnostic purposes. Rest assured, no personal information such as user email, name or any other field is collected.

To learn more about what data is collected, how we use it and how you can change the data collection setting [see details page](readme-assets/additional-docs/data_collection_and_use.md).


## Additional Resources

- [Kit SDK Companion Tutorial](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html)

- [Usage and Troubleshooting](readme-assets/additional-docs/usage_and_troubleshooting.md)

- [Developer Bundle Extensions](readme-assets/additional-docs/developer_bundle_extensions.md)

- [Omniverse Kit SDK Manual](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/index.html)


## Contributing

We provide this source code as-is and are currently not accepting outside contributions.