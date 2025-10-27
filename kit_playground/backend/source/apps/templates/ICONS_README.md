# Template Icons

## Current Status

Template icons are configured but the actual PNG files are stored in Git LFS and need to be pulled.

## Icon Locations

Application templates should have icons at:
- `templates/apps/{template_name}/assets/icon.png`

Extension templates should have icons at:
- `templates/extensions/{template_name}/template/data/icon.png`

## Pulling Icons from Git LFS

To get the actual icon images:

```bash
git lfs pull
```

## Icon Requirements

- Format: PNG
- Recommended size: 256x256 pixels or larger
- Should have transparent background for best results

## Current Icon Status

Application Templates:
- ✅ kit_base_editor - Icon configured (needs LFS pull)
- ✅ usd_composer - Icon configured (needs LFS pull)
- ✅ usd_explorer - Icon configured (needs LFS pull)
- ✅ usd_viewer - Icon configured (needs LFS pull)
- ✅ kit_service - Icon configured (needs LFS pull)

## UI Behavior

The UI will:
1. Display custom icons when available
2. Fall back to Material-UI icons (based on template type) when icons are missing
3. Show a gradient background with the template type icon

This provides a graceful degradation when icons aren't available.
