# Bug Fix Prompt

Use this prompt when fixing a bug.

## Investigation Steps

1. **Reproduce the Bug**
   - [ ] Identify exact steps to reproduce
   - [ ] Check which components are affected
   - [ ] Verify it's actually a bug (not expected behavior)

2. **Root Cause Analysis**
   - [ ] Review relevant code
   - [ ] Check recent changes (git log)
   - [ ] Look for similar issues
   - [ ] Identify why tests didn't catch it

3. **Write Regression Test**
   - [ ] Create test that reproduces the bug
   - [ ] Test should FAIL before fix
   - [ ] Test should PASS after fix

4. **Implement Fix**
   - [ ] Make minimal changes
   - [ ] Don't refactor while fixing
   - [ ] Ensure fix doesn't break other features

5. **Validate**
   - [ ] Regression test passes
   - [ ] All existing tests still pass
   - [ ] Manual verification
   - [ ] Check for edge cases

6. **Document**
   - [ ] Update relevant documentation
   - [ ] Add comments explaining the fix
   - [ ] Update TROUBLESHOOTING.md if common

## Commit Message Template

```
Fix: Brief description of bug

Issue: Describe the bug and its impact
Root Cause: Explain what was wrong
Solution: Explain the fix

Files Modified:
• path/to/file.py

Test Coverage:
• Added regression test: test_name
• All tests passing: X/Y

Closes #issue_number
```

## Common Bug Patterns

### Orphaned Processes
- Missing process group management
- Not cleaning up in test teardown

### Path Issues
- Not using Path.resolve()
- Directory traversal vulnerabilities

### JSON Mode
- Mixing stdout and stderr
- Not suppressing non-JSON output

### WebSocket
- Not unsubscribing from events
- Memory leaks in event handlers
