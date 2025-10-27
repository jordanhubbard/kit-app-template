# Documentation Index

Complete guide to all documentation in the Kit App Template repository.

## 📖 For Users

### Getting Started

1. **[README.md](../README.md)** - Start here
   - Overview and prerequisites
   - Quick start guide (CLI and UI)
   - Basic concepts

2. **[User Guide](./USER_GUIDE.md)** - Primary learning resource
   - Progressive examples (beginner to advanced)
   - Each example shown in CLI and UI
   - Complete workflows with explanations
   - **Read this if:** You want step-by-step tutorials

3. **[Quick Reference](./QUICK_REFERENCE.md)** - Command cheat sheet
   - Common commands
   - Configuration snippets
   - Troubleshooting quick fixes
   - **Use this when:** You need to look up a command quickly

### Visual Development

4. **[Kit Playground Guide](./KIT_PLAYGROUND_GUIDE.md)** - UI development environment
   - Interface tour with screenshots
   - Complete UI workflows
   - Panel system explained
   - Troubleshooting UI issues
   - **Read this if:** You're using the web-based interface

### Technical Reference

5. **[Architecture](./ARCHITECTURE.md)** - System design
   - How the system works
   - Component relationships
   - Extension system
   - **Read this if:** You want to understand the internals

6. **[Template System](./TEMPLATE_SYSTEM.md)** - Template details
   - Template structure
   - How templates work
   - Creating custom templates
   - **Read this if:** You're creating or modifying templates

7. **[API Documentation](./API_USAGE.md)** - API reference
   - REST endpoints
   - WebSocket events
   - Request/response formats
   - **Read this if:** You're integrating with the API

---

## 🔧 For Developers

### Implementation Guides

8. **[Enhanced Template Spec](./ENHANCED_TEMPLATE_SPEC.md)** - Template metadata
   - Template TOML format
   - Icon system
   - Documentation structure
   - **Read this if:** You're creating advanced templates

9. **[Template Design](./TEMPLATE_DESIGN.md)** - Template best practices
   - Design patterns
   - Variable substitution
   - File organization
   - **Read this if:** You're designing templates

10. **[Dynamic App Discovery](./DYNAMIC_APP_DISCOVERY.md)** - Application registry
    - How apps are discovered
    - Registration system
    - Metadata extraction
    - **Read this if:** You're working on the build system

---

## 🚀 Advanced Topics

### Feature Documentation

11. **[Per-App Dependencies](../ai-docs/PER_APP_DEPENDENCIES.md)** - Isolated dependencies
    - How per-app deps work
    - Migration guide
    - Benefits and trade-offs
    - **Read this if:** You need isolated dependency management

12. **[Standalone Projects](../ai-docs/STANDALONE_PROJECTS.md)** - Self-contained apps
    - What makes a project standalone
    - Distribution strategies
    - Use cases
    - **Read this if:** You're distributing applications

13. **[Kit App Streaming](../ai-docs/KIT_APP_STREAMING_DESIGN.md)** - Cloud streaming
    - Streaming architecture
    - WebRTC setup
    - Deployment options
    - **Read this if:** You're building cloud-streamed apps

---

## 🐛 Troubleshooting & Fixes

### Problem-Specific Guides

14. **[Build Streaming Fix](../ai-docs/BUILD_STREAMING_AND_LAUNCH_FIX.md)**
    - Why build output was buffered
    - PTY solution
    - Real-time streaming
    - **Read this if:** Build output isn't streaming

15. **[API Proxy Fix](../ai-docs/API_PROXY_FIX.md)**
    - Frontend/backend proxy setup
    - Port configuration
    - CORS handling
    - **Read this if:** API calls are failing (404s)

16. **[File Save Fix](../ai-docs/FILE_SAVE_FIX.md)**
    - Filesystem API
    - Permission handling
    - Editor integration
    - **Read this if:** File saving isn't working

17. **[Kit File Creation Bug Fix](../ai-docs/KIT_FILE_CREATION_BUG_FIX.md)**
    - Template generation issues
    - Path management
    - Test coverage
    - **Read this if:** Projects aren't creating .kit files

18. **[Panel Carousel System](../ai-docs/PANEL_CAROUSEL_SYSTEM.md)**
    - Dynamic panel management
    - Capacity calculation
    - Navigation system
    - **Read this if:** You're working on the UI panel system

---

## 📋 Process Documentation

### Development Workflow

19. **[Implementation Workflow](../ai-docs/IMPLEMENTATION_WORKFLOW.md)**
    - Development process
    - Testing strategy
    - Deployment steps

20. **[Commit Checklist](../ai-docs/COMMIT_CHECKLIST.md)**
    - Pre-commit checks
    - Testing requirements
    - Documentation updates

---

## 🎯 Quick Navigation Guide

### "I want to..."

**...create my first application**
→ Start with [README Quick Start](../README.md#-quick-start)
→ Then [User Guide - Example 1](./USER_GUIDE.md#example-1-creating-your-first-application)

**...use the visual interface**
→ [Kit Playground Guide](./KIT_PLAYGROUND_GUIDE.md)

**...find a specific command**
→ [Quick Reference](./QUICK_REFERENCE.md)

**...build an application**
→ [User Guide - Example 2](./USER_GUIDE.md#example-2-building-your-application)

**...create an extension**
→ [User Guide - Example 5](./USER_GUIDE.md#example-5-working-with-extensions)

**...create a standalone project**
→ [User Guide - Example 6](./USER_GUIDE.md#example-6-creating-standalone-projects)

**...understand the architecture**
→ [Architecture Guide](./ARCHITECTURE.md)

**...create a custom template**
→ [Template System](./TEMPLATE_SYSTEM.md) + [Template Design](./TEMPLATE_DESIGN.md)

**...integrate with the API**
→ [API Documentation](./API_USAGE.md)

**...troubleshoot build issues**
→ [User Guide - Troubleshooting](./USER_GUIDE.md#troubleshooting)
→ [Quick Reference - Common Issues](./QUICK_REFERENCE.md#common-issues)

**...troubleshoot UI issues**
→ [Kit Playground Guide - Troubleshooting](./KIT_PLAYGROUND_GUIDE.md#troubleshooting)

**...enable app streaming**
→ [Kit App Streaming Design](../ai-docs/KIT_APP_STREAMING_DESIGN.md)

**...manage per-app dependencies**
→ [Per-App Dependencies](../ai-docs/PER_APP_DEPENDENCIES.md)

**...distribute my application**
→ [User Guide - Package and Distribution](./USER_GUIDE.md#package-and-distribution)
→ [Standalone Projects](../ai-docs/STANDALONE_PROJECTS.md)

---

## 📚 Document Categories

### By Audience

**Beginners:**
- README.md
- User Guide
- Quick Reference
- Kit Playground Guide

**Intermediate:**
- Architecture
- Template System
- API Documentation

**Advanced:**
- Enhanced Template Spec
- Per-App Dependencies
- Standalone Projects
- Streaming Design

### By Format

**Tutorial Style (Step-by-step):**
- User Guide
- Kit Playground Guide

**Reference Style (Look-up):**
- Quick Reference
- API Documentation
- Template System

**Conceptual (Understanding):**
- Architecture
- Template Design
- Streaming Design

**Troubleshooting (Problem-solving):**
- User Guide - Troubleshooting section
- Kit Playground Guide - Troubleshooting section
- Individual fix documents in ai-docs/

---

## 🔄 Documentation Update Status

**Last Major Update:** 2024-10-27

**Recent Changes:**
- ✅ Created comprehensive [User Guide](./USER_GUIDE.md) with CLI + UI examples
- ✅ Created detailed [Kit Playground Guide](./KIT_PLAYGROUND_GUIDE.md)
- ✅ Created [Quick Reference](./QUICK_REFERENCE.md) cheat sheet
- ✅ Updated Quick Start section with correct ports and workflows
- ✅ All examples reflect current UI (panel system, carousel, streaming builds)
- ✅ Troubleshooting sections updated with latest fixes

**What's Current:**
- ✅ Port numbers (3000 for UI, 5000 for backend)
- ✅ Panel carousel navigation
- ✅ Real-time build output streaming
- ✅ Launch button workflow
- ✅ File save/edit functionality
- ✅ Template creation flow

**What to Update Next:**
- 🔄 Add screenshots to Kit Playground Guide
- 🔄 Add video tutorials/GIFs for common workflows
- 🔄 Expand API documentation with more examples
- 🔄 Create a migration guide for v1 to v2 users

---

## 📝 Documentation Standards

All documentation in this repository follows these standards:

### Style Guidelines

1. **Progressive Complexity** - Start simple, build to advanced
2. **Dual Format** - Show CLI and UI methods when applicable
3. **Real Examples** - Use concrete, runnable examples
4. **Clear Headings** - Scannable structure with ToC
5. **Code Blocks** - Syntax-highlighted, copy-pasteable
6. **Troubleshooting** - Include common issues and solutions

### Writing Style

- **Active Voice** - "Click the button" not "The button is clicked"
- **Direct Address** - Speak to "you" (the user)
- **Concise** - One concept per paragraph
- **Scannable** - Bullet points, tables, visual hierarchy
- **Professional** - Clear technical writing

### File Naming

- `UPPERCASE.md` - Major guides and references
- `PascalCase.md` - Feature-specific documentation
- `snake_case.md` - Internal/temporary documentation

---

## 🤝 Contributing to Documentation

### How to Improve Docs

1. **Found an error?** - Submit a PR with the fix
2. **Have a suggestion?** - Open an issue describing the improvement
3. **Want to add content?** - Follow the standards above
4. **Screenshots outdated?** - Provide updated screenshots in PRs

### Documentation PRs Should Include

- [ ] Clear description of what changed
- [ ] Why the change improves documentation
- [ ] Any affected related documents (update those too)
- [ ] Spellcheck and grammar check
- [ ] Test any code examples

---

## 📞 Getting Help

**If documentation doesn't answer your question:**

1. Check the **Troubleshooting** sections:
   - [User Guide - Troubleshooting](./USER_GUIDE.md#troubleshooting)
   - [Kit Playground Guide - Troubleshooting](./KIT_PLAYGROUND_GUIDE.md#troubleshooting)
   - [Quick Reference - Common Issues](./QUICK_REFERENCE.md#common-issues)

2. Search **existing issues** in the repository

3. Join the **Omniverse Forums**: https://forums.developer.nvidia.com/c/omniverse/

4. Check **Kit SDK Documentation**: https://docs.omniverse.nvidia.com/kit/

---

**Happy Learning! 📚✨**
