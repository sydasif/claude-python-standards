---
description: Generate a detailed README.md from the codebase
---

1. **Survey the project** — Identify the project type, language, framework, and build system from config files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.).
2. **Analyze structure** — List top-level directories and key files to understand module organization and architecture.
3. **Extract features** — From entry points, CLI definitions, API routes, exports, and tests, derive the main features the project provides.
4. **Determine setup steps** — Check for dependency files, environment variable requirements, Dockerfiles, and build scripts to produce accurate setup instructions.
5. **Find usage examples** — Look at test files, example directories, CLI help output, or integration tests for realistic usage patterns.
6. **Read existing docs** — Review any current README, CONTRIBUTING, or docs/ folder to preserve existing context and avoid regressions.
7. **Generate README.md** — Produce a file with sections: **Overview**, **Features**, **Prerequisites**, **Setup**, **Usage**, **Project Structure**, **Contributing**.
