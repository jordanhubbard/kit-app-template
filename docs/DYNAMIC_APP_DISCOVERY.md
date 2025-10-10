# Dynamic .kit App Discovery

## Overview

This repository uses dynamic discovery to automatically find and build `.kit` application files instead of maintaining a static list in `repo.toml`.

## Configuration

In `repo.toml`, the `[repo_precache_exts]` section uses `app_discovery_paths` to specify directories to scan:

```toml
[repo_precache_exts]
app_discovery_paths = [
    "${root}/_build/apps",
]
```

## How It Works

During the build process (`repo.sh build`), the system:

1. Scans all directories specified in `app_discovery_paths`
2. Recursively finds all `.kit` files
3. Runs extension precaching for each discovered app
4. No manual updates to `repo.toml` needed when creating new apps

## Benefits

- **No Manual Updates**: Create new apps via playground UI or manually without editing `repo.toml`
- **Empty _build Support**: Works correctly even when `_build/apps` is initially empty
- **Automatic Discovery**: New `.kit` files are automatically included in builds
- **Backwards Compatible**: Falls back to static `apps` list if `app_discovery_paths` not specified

## Implementation Details

The dynamic discovery is implemented in:
- `_repo/deps/repo_kit_tools/kit-template/tools/autopull/pull_extensions/tinypull.py`

**Note**: The dynamic discovery feature requires `repo_kit_tools` version 1.10.0 or later with the
`discover_kit_files()` function. The current packman dependency includes these modifications in the
local cache at `~/.cache/packman/chk/repo_kit_tools/1.10.0/`.

## Migration from Static Lists

### Old Configuration (Static)
```toml
apps = [
    "${root}/_build/apps/my_company.my_editor/my_company.my_editor.kit",
    "${root}/_build/apps/test_editor/test_editor.kit",
]
```

### New Configuration (Dynamic)
```toml
app_discovery_paths = [
    "${root}/_build/apps",
]
```

The static `apps` list is kept as a fallback for backwards compatibility but is no longer used when
`app_discovery_paths` is specified.
