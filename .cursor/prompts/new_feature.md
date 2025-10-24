# New Feature Development Prompt

Use this prompt when starting a new feature.

## Checklist

1. **Planning**
   - [ ] Create FEATURE_NAME_DESIGN.md
   - [ ] Break into phases if complex
   - [ ] Identify affected components (CLI, API, UI)
   - [ ] Plan backward compatibility strategy

2. **Testing (FIRST!)**
   - [ ] Create tests/feature_name/ directory
   - [ ] Write unit tests (should fail initially)
   - [ ] Write integration tests
   - [ ] Add compatibility tests if touching CLI

3. **Implementation**
   - [ ] Implement smallest increment
   - [ ] Make tests pass one at a time
   - [ ] Run linter continuously
   - [ ] Update docstrings and type hints

4. **Integration**
   - [ ] Test CLI, API, and UI together
   - [ ] Verify WebSocket events if applicable
   - [ ] Check error handling

5. **Documentation**
   - [ ] Update docs/README.md
   - [ ] Update docs/API_USAGE.md
   - [ ] Add inline comments for complex logic

6. **Validation**
   - [ ] Run full test suite: make test
   - [ ] Run compatibility tests: make test-compatibility
   - [ ] Manual testing in all interfaces
   - [ ] Check linting: flake8, eslint

7. **Commit**
   - [ ] Clear, structured commit message
   - [ ] Create PHASE_X_COMPLETE.md for major features

## Template Questions

- What is the feature goal?
- Which components are affected?
- What are the backward compatibility implications?
- What tests are needed?
- What documentation needs updating?
