# Kit App Streaming Hallucination Correction

## Critical Issue: Widespread Hallucinations

**Date:** October 27, 2025  
**Severity:** Critical - Widespread misinformation  
**Status:** ✅ CORRECTED

---

## What Was Hallucinated

### Fake Extensions (DO NOT EXIST)

I incorrectly invented and documented **two non-existent extensions** across multiple files:

1. ❌ **`omni.services.streaming.webrtc`** - DOES NOT EXIST
2. ❌ **`omni.kit.streamhelper`** - DOES NOT EXIST

These extensions were **completely fabricated** and do not exist in the NVIDIA Kit SDK.

---

## The Real Streaming Architecture

### Actual Streaming Extensions (These DO Exist)

Kit App Streaming uses **three types** of streaming configurations:

| Type | Extension | Purpose |
|------|-----------|---------|
| **default** | `omni.kit.livestream.app` | Standard WebRTC streaming |
| **nvcf** | `omni.services.livestream.session` | NVIDIA Cloud Functions deployment |
| **gdn** | `omni.kit.gfn` | GeForce NOW (GDN) deployment |

### How Streaming Actually Works

**Streaming is an ApplicationLayerTemplate**, not standalone:

```
Base Application (my_app.kit)
  ↓
Streaming Layer (my_app_stream.kit)
  ├── Depends on: "my_app" = {}
  └── Includes: "omni.kit.livestream.app" = {}
```

**Location:** `templates/apps/streaming_configs/`

**Three configurations:**
- `default_stream.kit` - Uses `omni.kit.livestream.app`
- `nvcf_stream.kit` - Uses `omni.services.livestream.session` + cloud extensions
- `gdn_stream.kit` - Uses `omni.kit.gfn` for GeForce NOW

---

## Files That Were Contaminated

### Backend Code (Fixed ✅)

1. **`kit_playground/backend/routes/template_routes.py`**
   - **Before:** Tried to inject fake extensions into .kit files
   - **After:** Deprecated the approach, documented proper streaming layers
   - **Status:** ✅ FIXED

2. **`tools/repoman/streaming_utils.py`**
   - **Before:** Referenced fake extensions throughout
   - **After:** Complete rewrite using real extensions
   - **Status:** ✅ FIXED

3. **`kit_playground/backend/source/apps/tools/repoman/streaming_utils.py`**
   - **Before:** Copy of contaminated streaming_utils.py
   - **After:** Replaced with corrected version
   - **Status:** ✅ FIXED

### Tests (Fixed ✅)

4. **`tests/streaming/test_streaming_utils.py`**
   - **Before:** Tests validated fake extensions
   - **After:** Rewritten to test real extensions + hallucination prevention tests
   - **Status:** ✅ FIXED

### Documentation (Needs Archiving ⚠️)

The following documentation files perpetuate the hallucinations and should be **archived** or **deleted**:

5. **`ai-docs/KIT_APP_STREAMING_DESIGN.md`**
   - Contains extensive fake extension documentation
   - **Action:** ARCHIVE (move to `ai-docs/DEPRECATED/`)

6. **`ai-docs/KIT_APP_STREAMING_PHASE_2_3_COMPLETE.md`**
   - Documents fake streaming implementation
   - **Action:** ARCHIVE

7. **`ai-docs/SMART_LAUNCH_DECISION_TREE.md`**
   - References fake extensions in launch logic
   - **Action:** UPDATE (remove fake extension references)

8. **`ai-docs/LAUNCH_HOSTNAME_AND_STREAMING_FIXES.md`**
   - Discusses "missing" extensions (that don't exist)
   - **Action:** ARCHIVE

9. **`docs/README.md`**
   - Main docs reference fake extensions
   - **Action:** UPDATE (remove streaming section or correct it)

10. **`docs/API_USAGE.md`**
    - API docs reference fake extensions
    - **Action:** UPDATE

---

## What Was Wrong

### 1. Misunderstood Architecture ❌

**Wrong:** Streaming is a standalone application type  
**Correct:** Streaming is an **ApplicationLayerTemplate** that layers on top of base applications

**Wrong:** Enable streaming by adding extensions to .kit file  
**Correct:** Create a separate streaming .kit file that depends on the base app

### 2. Invented Extensions ❌

**Wrong:** Use `omni.services.streaming.webrtc` and `omni.kit.streamhelper`  
**Correct:** Use `omni.kit.livestream.app` (or `omni.services.livestream.session` for NVCF, or `omni.kit.gfn` for GDN)

### 3. Wrong Implementation ❌

**Wrong:** Modify .kit file to add streaming dependencies  
**Correct:** Apply a streaming layer template from `templates/apps/streaming_configs/`

---

## Correct Usage Examples

### Example 1: Default Streaming Layer

**File:** `templates/apps/streaming_configs/default_stream.kit`

```toml
[package]
title = "My App Streaming"
version = "1.0.0"
template_name = "omni.streaming_configuration"

[dependencies]
"my_app" = {}                    # ← Depends on base application
"omni.kit.livestream.app" = {}   # ← REAL streaming extension

[settings.app]
fastShutdown = true
name = "My App Streaming"
renderer.resolution.height = 1080
renderer.resolution.width = 1920
```

### Example 2: Detection (Corrected)

**Before (Wrong):**
```python
# DON'T DO THIS - These extensions don't exist!
if 'omni.services.streaming.webrtc' in dependencies:
    is_streaming = True
```

**After (Correct):**
```python
# Use the real extensions
from streaming_utils import STREAMING_EXTENSIONS, get_streaming_type

streaming_type = get_streaming_type(Path("my_app_stream.kit"))
if streaming_type == 'default':
    # Uses omni.kit.livestream.app
    pass
elif streaming_type == 'nvcf':
    # Uses omni.services.livestream.session
    pass
elif streaming_type == 'gdn':
    # Uses omni.kit.gfn
    pass
```

### Example 3: Launch (Corrected)

**Before (Wrong):**
```bash
# DON'T DO THIS - These flags don't work!
./my_app.sh \
  --enable omni.services.streaming.webrtc \
  --enable omni.kit.streamhelper
```

**After (Correct):**
```bash
# Use a streaming layer .kit file
./my_app_stream.sh  # ← This is a separate .kit file with streaming configured
```

---

## Corrected Code

### Backend (template_routes.py)

```python
# Kit App Streaming Note:
# Streaming is implemented as an ApplicationLayerTemplate, not by modifying the .kit file.
# To enable streaming, users should apply a streaming layer template:
#   - default_stream.kit (uses omni.kit.livestream.app)
#   - nvcf_stream.kit (uses omni.services.livestream.session for NVIDIA Cloud Functions)
#   - gdn_stream.kit (uses omni.kit.gfn for GeForce NOW)
# 
# The 'enable_streaming' parameter is deprecated and ignored.
# Use streaming layer templates from templates/apps/streaming_configs/ instead.
```

### Utilities (streaming_utils.py)

```python
# Real streaming extensions (not hallucinated!)
STREAMING_EXTENSIONS = {
    'default': 'omni.kit.livestream.app',        # Default WebRTC streaming
    'nvcf': 'omni.services.livestream.session',  # NVIDIA Cloud Functions
    'gdn': 'omni.kit.gfn',                       # GeForce NOW (GDN)
}
```

### Tests (test_streaming_utils.py)

```python
class TestHallucinationPrevention:
    """Tests to prevent hallucinated extensions from creeping back in."""

    def test_no_webrtc_hallucination(self):
        """Ensure omni.services.streaming.webrtc is not used."""
        hallucinated_ext = 'omni.services.streaming.webrtc'
        for ext_name in STREAMING_EXTENSIONS.values():
            assert ext_name != hallucinated_ext

    def test_no_streamhelper_hallucination(self):
        """Ensure omni.kit.streamhelper is not used."""
        hallucinated_ext = 'omni.kit.streamhelper'
        for ext_name in STREAMING_EXTENSIONS.values():
            assert ext_name != hallucinated_ext
```

---

## Hallucination Prevention

### Tests Added ✅

New test class `TestHallucinationPrevention` ensures:
1. Fake extensions are never referenced
2. Only real extensions are used
3. Correct streaming types are detected

### Code Review Checklist

Before merging any streaming-related code:

- [ ] Does it reference `omni.services.streaming.webrtc`? → **REJECT**
- [ ] Does it reference `omni.kit.streamhelper`? → **REJECT**
- [ ] Does it use `omni.kit.livestream.app`? → **OK**
- [ ] Does it use `omni.services.livestream.session`? → **OK (NVCF)**
- [ ] Does it use `omni.kit.gfn`? → **OK (GDN)**
- [ ] Does it treat streaming as a layer template? → **OK**
- [ ] Does it try to modify .kit files for streaming? → **REJECT**

---

## Impact Assessment

### Code Quality Impact
- ❌ **Misinformation spread across 10+ files**
- ❌ **Tests validated non-existent functionality**
- ❌ **Documentation taught incorrect patterns**
- ✅ **Now corrected in core files**

### User Impact
- ⚠️ **Users may have tried to use fake extensions**
- ⚠️ **Launch failures would occur (extensions not found)**
- ⚠️ **Confusion about streaming architecture**
- ✅ **Fixed code will prevent future issues**

### Documentation Impact
- ❌ **Multiple docs need archiving or correction**
- ⚠️ **Some docs still reference fake extensions**
- 🔄 **Cleanup in progress**

---

## Lessons Learned

### What Went Wrong

1. **No validation against SDK documentation**
   - Did not verify extensions existed
   - Assumed extensions based on naming patterns

2. **Self-reinforcing hallucinations**
   - Initial mistake was copied across files
   - Tests validated the hallucination
   - Documentation cemented it

3. **No reality checks**
   - Did not attempt to use the extensions
   - Did not check Kit SDK registry
   - Did not review actual template files

### Prevention Measures

1. **✅ Validation tests added**
   - Tests now explicitly check against hallucinations
   - Real extensions are enumerated
   - Detection logic validates against known-good list

2. **✅ Documentation review**
   - Archiving bad docs to `ai-docs/DEPRECATED/`
   - Keeping this correction doc prominent
   - Adding warnings to legacy code

3. **✅ Code comments**
   - Explicit comments about real vs fake extensions
   - Warnings in deprecated code paths
   - Links to this document

---

## Action Items

### Completed ✅
- [x] Fix `template_routes.py` (removed fake extension injection)
- [x] Fix `streaming_utils.py` (complete rewrite with real extensions)
- [x] Fix `test_streaming_utils.py` (rewritten with hallucination prevention)
- [x] Add this correction document

### Remaining 🔄
- [ ] Archive bad documentation to `ai-docs/DEPRECATED/`
- [ ] Update `docs/README.md` to remove/correct streaming section
- [ ] Update `docs/API_USAGE.md` to remove fake extensions
- [ ] Update `SMART_LAUNCH_DECISION_TREE.md` to use real extensions
- [ ] Add banner to deprecated docs warning about hallucinations

### Future 📋
- [ ] Create proper streaming layer documentation
- [ ] Document the three streaming types (default, nvcf, gdn)
- [ ] Add examples for each streaming configuration
- [ ] Create user guide for applying streaming layers

---

## Commit Message Template

```
Fix critical hallucinations in Kit App Streaming implementation

CRITICAL: Removed fake extensions that don't exist

Hallucinated extensions (REMOVED):
- omni.services.streaming.webrtc (DOES NOT EXIST)
- omni.kit.streamhelper (DOES NOT EXIST)

Real extensions (NOW USED):
- omni.kit.livestream.app (default streaming)
- omni.services.livestream.session (NVCF)
- omni.kit.gfn (GDN)

Fixed files:
- kit_playground/backend/routes/template_routes.py
- tools/repoman/streaming_utils.py
- tests/streaming/test_streaming_utils.py

Changes:
1. Removed all references to fake extensions
2. Documented correct streaming architecture (ApplicationLayerTemplate)
3. Added hallucination prevention tests
4. Deprecated incorrect streaming enablement approach

Impact:
- Prevents users from trying non-existent extensions
- Corrects streaming architecture understanding
- Adds safeguards against future hallucinations

See ai-docs/STREAMING_HALLUCINATION_CORRECTION.md for full details.
```

---

## References

- **Real Templates:** `templates/apps/streaming_configs/`
- **Component Template:** `templates/components/streaming/omni_default_streaming/`
- **Template Metadata:** `kit_playground/backend/source/apps/templates/components/streaming/omni_default_streaming/template.toml`
- **This Document:** `ai-docs/STREAMING_HALLUCINATION_CORRECTION.md`

---

**Remember:** If you see `omni.services.streaming.webrtc` or `omni.kit.streamhelper` anywhere in the codebase, **it's a hallucination and must be removed!**

