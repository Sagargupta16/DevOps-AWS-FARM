# Changelog

## [1.5.1] - 2026-10-21

### Changed

- README diagrams drawn with [orrery](https://github.com/Sagargupta16/orrery): the `deploy.yml` pipeline at the top (GitHub Actions to the IAM deploy role, Amazon ECR and Amazon ECS, with everything behind `DEPLOY_ENABLED` dashed) and the application under Architecture, each in a light and a dark version. They replace the two Mermaid diagrams. The specs live in `assets/diagrams/*.yaml` with an `evidence:` path on every node, because `/docs/` is gitignored

## [1.5.0] - 2026-10-18

### Added

- `GET /health`: pings MongoDB with a 2 second timeout and returns 200 `{"status": "ok", "database": "up"}` or 503 `{"status": "unavailable", "database": "down"}`. Used by the Docker `HEALTHCHECK`, the ECS task definition template and the ALB target group
- Structured logs: `LOG_FORMAT=json` (the image default) writes one JSON object per line, and a middleware logs method, path, status and `duration_ms` for every request
- Email is unique: a unique index created at startup plus a pre-check return 409 on create, and on update when the email belongs to another user
- `scripts/seed.py` loads demo users and posts through the API (standard library only, idempotent). `--url` only accepts http(s) on localhost, 127.0.0.1 or ::1, and demo passwords are random per run
- README screenshots at desktop (1440x900) and phone (390x844) widths, captured by `client/scripts/screenshots.mjs` (Playwright, `npm run screenshots`)
- `aws/`: GitHub OIDC trust policy, least-privilege deploy role policy, Fargate task definition template and a setup and teardown guide

### Changed

- `deploy.yml` deploys for real when `DEPLOY_ENABLED=true`: GitHub OIDC instead of AWS access keys, a `production` environment, the image tagged with the commit SHA (reused on re-runs), the task definition rendered from its family, `amazon-ecs-deploy-task-definition` waiting for stability, and a `/health` smoke test. The four AWS actions are pinned to commit SHAs. Its configuration moved from secrets to repo variables (`AWS_ROLE_ARN`, `AWS_REGION`, `ECR_REPOSITORY`, `ECS_CLUSTER`, `ECS_SERVICE`, `ECS_TASK_FAMILY`, `ECS_CONTAINER_NAME`, `APP_URL`)
- `deploy.yml` tests are blocking again and run against the MongoDB service container instead of `secrets.MONGODB_URL`
- `main.yml`: the commented AWS credentials step uses OIDC (`role-to-assume`) instead of access keys
- Both Dockerfiles, `deploy.yml` and `main.yml` install `requirements.lock.txt` with `--require-hashes --only-binary :all:`; npm installs in CI and the image use `npm ci --ignore-scripts`
- Images are based on `python:3.14-slim` instead of alpine (pymongo publishes no musllinux wheel, so alpine compiled it with gcc) and the app runs as a non-root user
- One cached `MongoClient` per process instead of a new client per `get_database()` call
- The app starts without `client_build/` and serves the API only, with a warning
- Tests rewritten: 31 HTTP-level tests through FastAPI's `TestClient` with `pytest.raises`, cleaning up only the documents they created. The old suite passed even when nothing raised, and one test deleted every user named `test`
- Vite dev proxy forwards `/health`

## [1.4.0] - 2026-10-18

### Fixed

- Creating or updating a user no longer crashes with a 500: passlib 1.7.4 raised `ValueError` on every hash under bcrypt 5. Hashing now calls `bcrypt` directly and passlib is removed
- Passwords over 72 bytes (bcrypt's limit) are rejected with a 422 instead of crashing
- `GET /user` and `GET /blog` return an empty list instead of 404 when there are no records, so the UI no longer shows an error on a fresh database
- The dev client called `http://localhost:8000` cross-origin and failed on CORS; it now uses the Vite proxy (same-origin)
- The client's error banner clears on the next successful load
- `docker compose up` works out of the box: adds a `mongo:8.2` service with a healthcheck, passes `MONGODB_URL` to the tests and app, and starts the app only after the tests pass

### Security

- Stop logging the MongoDB connection URL (CodeQL `py/clear-text-logging-sensitive-data`); only its source (env var, secrets file or local default) is logged
- Raise the `pymongo` floor to 4.18.2 (CVE-2026-96748, CVE-2026-96749 high; CVE-2026-88029, CVE-2026-96747, CVE-2024-5629 medium)
- `ci.yml` installs from `requirements.lock.txt`, a hash-locked pin of the full tree, with `--require-hashes --only-binary :all:`
- Pin the third-party actions in `main.yml` to full commit SHAs: sonarqube-scan-action v8.3.0, setup-buildx-action v4.4.1
- Exclude `config/secrets.yml`, `.env.*`, virtualenvs, `node_modules` and build output from the Docker build context so credentials are not baked into the image
- Remove the `/var/run/docker.sock` mount from the app container
- Add least-privilege `permissions: contents: read` to all workflows (CodeQL `actions/missing-workflow-permissions`); the black auto-format job gets explicit write scopes

### Changed

- `ci.yml` now runs the pytest suite against a MongoDB 8.2 service container with the 80% coverage gate on every push and PR
- Bump GitHub Actions: checkout v7, setup-python v7, setup-node v7, upload-artifact v7, download-artifact v8, setup-buildx-action v4; pin sonarqube-scan-action to v8.3.0 instead of `@master`
- Bump client to Vite 8, @vitejs/plugin-react 6, React 19.3 and the axios floor to 1.20
- Add `pyyaml` to requirements.txt (imported directly); drop the non-existent `pymongo[srv]` extra and the Dockerfile's cython and `pyyaml==6.0.1` installs (no Python 3.14 wheel, forced a source build)
- Pydantic v2 cleanup: `ConfigDict(from_attributes=True)` and `model_dump()` replace `orm_mode` and `.dict()`
- `main.yml`: branch references point at `main`, step labels match the installed versions, the bot commit identity replaces a stale personal email
- README: corrected endpoint paths and status codes, removed claims the code does not back (authentication, VS Code task, push-to-deploy), added Mermaid architecture and pipeline diagrams, a workflow table and tech decisions

## [1.3.5] - 2026-10-06

- Bump axios to 1.20.0 and resolve the open Dependabot alerts (#151, #152)

## [1.3.4] - 2026-09-03

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
