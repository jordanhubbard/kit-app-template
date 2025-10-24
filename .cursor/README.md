# .cursor Directory Structure

This directory contains Cursor AI configuration and context for the Kit App Template project.

## Structure

```
.cursor/
├── README.md              # This file
├── rules                  # Main rules file (project guidelines)
├── context/               # Context files for specific domains
│   ├── testing.md        # Testing patterns and best practices
│   ├── architecture.md   # System architecture overview
│   └── streaming.md      # Kit App Streaming specifics
└── prompts/              # Reusable prompts for common tasks
    ├── new_feature.md    # Checklist for new features
    ├── bug_fix.md        # Bug fix workflow
    └── debugging.md      # Debugging guide
```

## How to Use

### Main Rules (`rules`)
The primary configuration file that Cursor AI uses automatically. Contains:
- Architectural principles
- Code style guidelines
- Testing requirements
- Security best practices
- Commit message formats
- Critical rules (never violate)

### Context Files (`context/`)
Domain-specific reference information:

- **testing.md**: Process management, test markers, coverage requirements
- **architecture.md**: Three-tier architecture, data flow, design patterns
- **streaming.md**: Kit App Streaming implementation details

Use these when working on specific features or debugging issues in that domain.

### Prompts (`prompts/`)
Task-specific checklists and workflows:

- **new_feature.md**: Complete workflow for adding new features
- **bug_fix.md**: Step-by-step bug fix process
- **debugging.md**: Quick diagnostic commands and common issues

Invoke these prompts when starting a new task to ensure you follow best practices.

## Usage Examples

### Starting a New Feature
1. Review `.cursor/prompts/new_feature.md`
2. Check relevant context in `.cursor/context/`
3. Follow the checklist
4. Reference `.cursor/rules` for code style

### Fixing a Bug
1. Use `.cursor/prompts/bug_fix.md` workflow
2. Check `.cursor/prompts/debugging.md` for diagnostics
3. Write regression test first
4. Follow commit format from `.cursor/rules`

### Working with Tests
1. Review `.cursor/context/testing.md`
2. Use process group pattern (CRITICAL!)
3. Add appropriate pytest markers
4. Run compatibility tests before CLI changes

### Adding Kit App Streaming Features
1. Check `.cursor/context/streaming.md` for implementation details
2. Follow three-tier pattern: CLI → API → UI
3. Test all three interfaces
4. Update streaming documentation

## Maintenance

This directory should be updated when:
- New architectural patterns emerge
- Common mistakes are identified
- Best practices evolve
- New features require specific context

**Last Updated**: October 24, 2025

## Related Documentation

- **Design Docs**: See `PHASE_*.md` files in project root
- **API Docs**: `docs/API_USAGE.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Testing**: `tests/` directory with comprehensive test suite

## Philosophy

The `.cursor` directory embodies the project's commitment to:
- **Backward Compatibility**: Never break existing behavior
- **Test-First Development**: Write tests before code
- **Comprehensive Documentation**: Keep docs current
- **Security**: Validate all inputs
- **Clean Code**: Lint, type hints, clear naming

These aren't just guidelines—they're the foundation of the project's success.
