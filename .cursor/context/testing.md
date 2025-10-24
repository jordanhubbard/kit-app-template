# Testing Context for Kit App Template

## Process Management Pattern (CRITICAL)

Always use process groups when launching Kit applications:

```python
import os
import signal
import subprocess

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=os.setsid  # Create new process group
)

# Cleanup entire process tree
try:
    pgid = os.getpgid(process.pid)
    os.killpg(pgid, signal.SIGTERM)
    process.wait(timeout=5)
except subprocess.TimeoutExpired:
    os.killpg(pgid, signal.SIGKILL)
    process.wait(timeout=2)
```

Why? Kit apps spawn child processes. Without process groups, orphaned processes cause test failures and tool timeouts.

## Test Markers

- `@pytest.mark.slow` - Tests >5 seconds (builds, launches)
- `@pytest.mark.quick` - Fast tests <1 second
- `@pytest.mark.compatibility` - Baseline compatibility tests

## Test Commands

```bash
pytest tests/ -v -m "not slow"           # Fast tests
pytest tests/ -v -m "slow"               # Slow tests
make test-compatibility                  # Compatibility baseline
make test                                # All tests
```

## Coverage Requirements

- New features: >95% coverage
- Bug fixes: Add regression test
- Refactoring: Maintain existing coverage
