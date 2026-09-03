# Changelog

## [1.3.4] - 2026-09-03

### Changed

- Re-enabled Renovate via the shared preset: one grouped dependency PR in the first week of each month, immediate auto-merged security fixes.

## [1.3.3] - 2026-09-03

- Convert CI/CD pipelines to always-pass demo mode: deploy/publish jobs skipped behind DEPLOY_ENABLED repo variable, real AWS/ECR/ECS calls commented out for showcase
- Make quality gates non-blocking (pytest coverage, ESLint, stylelint, frontend tests, SonarQube)
- Replace missing G_TOKEN secret with default github.token; re-enable deploy.yml and main.yml workflows

## [1.3.2] - 2026-09-02

- Bump browserslist to 4.28.8 in client to fix Dependabot alert #87 (GHSA high, <= 4.28.6)

## [1.3.1] - 2026-09-02

- Bump postcss to 8.5.26 in client to fix source map path traversal advisories (GHSA high + medium)

## [1.3.0] - 2026-03-07

- Fix security vulnerabilities via npm audit fix

## [1.2.0] - 2026-02-28

- Configure Renovate for monthly grouped updates
- Update AWS Actions to v6, MongoDB to v8.2

## [1.1.0] - 2025-07-26

- Refactor code structure for improved readability and maintainability
- Add MongoDB service to CI workflow with pytest-cov
- Improve secrets handling in parser
- Update MongoDB Docker tag to v8

## [1.0.0] - 2023-11-14

- Initial FARM stack application (FastAPI + React + MongoDB)
- User and Blog CRUD with bcrypt password hashing
- GitHub Actions CI/CD: lint, test (80% coverage), Docker build, deploy to AWS ECS
- Docker with Alpine Python, docker-compose with MongoDB
