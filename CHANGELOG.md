# Changelog

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
