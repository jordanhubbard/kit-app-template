# Kit SDK Tooling Guide

This document provides an overview of the practical aspects of using the tooling provided in the `kit-app-template`. Intended for users with a basic familiarity with command-line operations, this guide offers typical usage patterns and recommendations for effective tool use. For a complete list of options for a given tool, use the help command: `./repo.sh [tool] -h` or `.\repo.bat [tool] -h`.

## Overview of Tools

The `kit-app-template` repository includes several tools designed to streamline the development of applications and extensions within the Omniverse Kit SDK.

### Available Tools
- `template`
- `build`
- `launch`
- `test`
- `package`

Each tool plays a specific role in the development workflow:

## Template Tool

**Command:** `./repo.sh template` or `.\repo.bat template`

### Purpose
The template tool facilitates the initiation of new projects by generating scaffolds for applications or extensions based on predefined templates. Templates are organized in the `/templates/` directory with configuration defined in `templates/template_registry.toml`.

### Project Output Location
By default, applications and microservices are created in `_build/apps/` with each project in its own directory:
```
_build/apps/
└── {project_name}/
    ├── {project_name}.kit      # Main application configuration
    ├── README.md               # Template documentation
    ├── .project-meta.toml      # Project metadata
    ├── repo.sh                 # Linux wrapper script
    └── repo.bat                # Windows wrapper script
```

This structure separates build artifacts from source code and provides proper project organization. Each project directory includes wrapper scripts that allow running repository commands from within the project directory.

### Usage
The template tool has four main commands: `list`, `docs`, `new`, `replay`, and `modify`.

#### `list`
Lists available templates without initiating the configuration wizard. You can optionally filter by template type.

**Linux:**
```bash
# List all templates
./repo.sh template list

# List templates by type
./repo.sh template list --type application
./repo.sh template list --type extension
./repo.sh template list --type microservice
```
**Windows:**
```powershell
# List all templates
.\repo.bat template list

# List templates by type
.\repo.bat template list --type application
.\repo.bat template list --type extension
.\repo.bat template list --type microservice
```

#### `docs`
Display comprehensive documentation for a specific template, including use cases, features, and getting started instructions.

**Linux:**
```bash
./repo.sh template docs kit_base_editor
./repo.sh template docs kit_service
```
**Windows:**
```powershell
.\repo.bat template docs kit_base_editor
.\repo.bat template docs kit_service
```

#### `new`
Creates new applications or extensions from templates with interactive prompts guiding you through various configuration choices.

**Interactive Mode:**

**Linux:**
```bash
./repo.sh template new
```
**Windows:**
```powershell
.\repo.bat template new
```

**Non-Interactive Mode with Arguments:**

You can provide all configuration via command-line arguments for automation:

**Linux:**
```bash
./repo.sh template new kit_base_editor --name my_company.my_app --display-name "My Application" --version 1.0.0
```
**Windows:**
```powershell
.\repo.bat template new kit_base_editor --name my_company.my_app --display-name "My Application" --version 1.0.0
```

**Standalone Projects:**

Use `--output-dir` to create a self-contained project outside the repository:

**Linux:**
```bash
./repo.sh template new kit_service --name my_company.my_api --display-name "My API" --output-dir /path/to/project
```
**Windows:**
```powershell
.\repo.bat template new kit_service --name my_company.my_api --display-name "My API" --output-dir C:\path\to\project
```

**Note:** Only application and microservice templates support standalone project generation. Extension templates must be part of an application.

#### `replay`
In cases where automation is required for CI pipelines or other scripted workflows, it is possible to record and replay the `template new` configuration.

To achieve this first run template new with the `--generate-playback` flag:

**Linux:**
```bash
./repo.sh template new --generate-playback {playback_file_name}.toml
```

**Windows:**
```powershell
.\repo.bat template new --generate-playback {playback_file_name}.toml
```

After the configuration has been generated, the configuration can be replayed using the `replay` command:

**Linux:**
```bash
./repo.sh template replay {playback_file_name}.toml
```

**Windows:**
```powershell
.\repo.bat template replay {playback_file_name}.toml
```

#### `modify`
The `modify` command lets you add one or more Application Template Layers (for example, streaming support) to an existing application that was not originally configured with them.

**Linux:**
```bash
./repo.sh template modify
```
**Windows:**
```powershell
.\repo.bat template modify
```

When prompted, select the Application `.kit` file you want to update.

Next, select (using Space) the Template Layer(s) to add. Enter to confirm.

After the operation completes, rebuild (`./repo.sh build` or `.\repo.bat build`) the project to pull in the new extensions.

## Build Tool

**Command:** `./repo.sh build` or `.\repo.bat build`

### Purpose
The build tool compiles all necessary files in your project, ensuring they are ready for execution, testing, or packaging. It includes all resources located in the `source/` directory.

### Usage
Run the build command before testing or packaging your application to ensure all components are up to date:

**Linux:**
```bash
./repo.sh build
```
**Windows:**
```powershell
.\repo.bat build
```

Other common build options:
- **`-c` or `--clean`:** Cleans the build directory before building.
- **`x` or `--rebuild`:** Rebuilds the project from scratch.

## Launch Tool

**Command:** `./repo.sh launch` or `.\repo.bat launch`

### Purpose
The launch tool is used to start your application after it has been successfully built, allowing you to test it live.

### Usage
Select and run a built .kit file from the `_build/apps` directory:

**Linux:**
```bash
# Interactive: select from available applications
./repo.sh launch

# Direct: launch a specific application
./repo.sh launch --name my_company.my_app
```
**Windows:**
```powershell
# Interactive: select from available applications
.\repo.bat launch

# Direct: launch a specific application
.\repo.bat launch --name my_company.my_app
```

**Launch from Project Directory:**

You can also launch an application directly from its project directory using the wrapper scripts:

```bash
cd _build/apps/my_company.my_app
./repo.sh launch
```

Additional launch options:
- **`-d` or `--dev-bundle`:** By default, the templates in the Kit App Template repository include `omni.kit.developer.bundle` in their `.kit` file definitions. If you want to exclude it from your application definition, you can still enable it at launch by using the `-d` or `--dev-bundle` flags. This approach prevents the developer bundle extensions from being packaged and sent to customers, while allowing you to use them during development.

- **`-p` or `--package`:** Launches a packaged application from a specified path.

    **Linux:**
    ```bash
    ./repo.sh launch -p </path/to/package.zip>
    ```
    **Windows:**
    ```powershell
    .\repo.bat launch -p <C:\path\to\package.zip>
    ```

- **`--container`:** Launches a containerized application (Linux only).

    **Linux:**
    ```bash
    ./repo.sh launch --container
    ```
    **Windows:**
    ```powershell
    .\repo.bat launch --container
    ```

- **Passing args to launched Kit executable:**
You can pass through arguments to your targeted Kit executable by appending `--` to your launch command. Any flags added after `--` will be passed through to Kit directly. The following examples will pass the `--clear-cache` flag to Kit.

    **Linux:**
    ```bash
    ./repo.sh launch -- --clear-cache
    ```
    **Windows:**
    ```powershell
    .\repo.bat launch -- --clear-cache
    ```
    
:warning: **Important Notes When Launching Applications:** 
- **Launching an application with path specific arguments:** When launching application with path specific args (for example `--/app/auto_load_usd` using the USD Viewer Template), the path provided should either be absolute (full path from root) or if the asset is within an extension use a tokenized path (e.g. `./repo.sh launch -- --/app/auto_load_usd='${omni.usd_viewer.samples}/samples_data/stage01.usd'` )

- **Launching directly from an uncompressed package:** The `launch` utility is accessible from the project repository and can be used to launch packages from the project repository.  **However**, if launching an application from within a uncompressed packaged the `launch` utility is not available and any arguments passed should be passed to the `.bat` or `.sh` script directly (e.g. `my.app.kit.sh --/app/auto_load_usd=path/to/asset.usd`).

## Test Tool

**Command:** `./repo.sh test` or `.\repo.bat test`

### Purpose
The test tooling facilitates the execution of automated tests on your applications and extensions to help ensure their functionality and stability.  Applications configurations (`.kit` files) are tested to ensure they can startup and shutdown without issue.  However, the tests written within the extensions will dictate a majority of application functionality testing.  Extension templates provided by the Kit App Template repository include sample tests which can be expanded upon to increase test coverage as needed.

### Usage
Always run a build before testing:

**Linux:**
```bash
./repo.sh test
```
**Windows:**
```powershell
.\repo.bat test
```

## Package Tool

**Command:** `./repo.sh package` or `.\repo.bat package`

### Purpose
This tool prepares your application for distribution or deployment by packaging it into a distributable format.

### Usage
Always run a build before packaging to ensure the application is up-to-date:

**Linux:**
```bash
./repo.sh package
```
**Windows:**
```powershell
.\repo.bat package
```


Additional launch options:
- **`-n` or `--name`:** Specifies the package (or container image) name.

    **Linux:**
    ```bash
    ./repo.sh package -n <package_name>
    ```
    **Windows:**
    ```powershell
    .\repo.bat package -n <package_name>
    ```

- **`--thin`:** Creates a thin package that includes only custom extensions and configurations for required registry extensions.

    **Linux:**
    ```bash
    ./repo.sh package --thin
    ```
    **Windows:**
    ```powershell
    .\repo.bat package --thin
    ```

- **`--container`:** Packages the application as a container image (Linux only). When using the `--container` flag, the user will be asked to select a `.kit` file to use within the entry point script for the container.  This can also be specified without user interaction by passing it appropriate `.kit` file name via the `--target-app` flag.

    **Linux:**
    ```bash
    ./repo.sh package --container
    ```
    **Windows:**
    ```powershell
    .\repo.bat package --container
    ```

:warning: **Important Note for Packaging:** Because the packaging operation will package everything within the `source/` directory the package version will need to be set independently of a given `kit` file.  **The version is set within the `tools/VERSION.md` file.**

## Additional Resources
- [Kit SDK Companion Tutorial](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/docs/intro.html)