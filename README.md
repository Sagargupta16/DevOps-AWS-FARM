# DevOps-AWS-FARM

[![CI](https://github.com/Sagargupta16/DevOps-AWS-FARM/actions/workflows/ci.yml/badge.svg)](https://github.com/Sagargupta16/DevOps-AWS-FARM/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A FARM-stack app (FastAPI, React 19, MongoDB) packaged as a single Docker image, with GitHub Actions pipelines: lint, test and build on every push and pull request, plus a manually dispatched pipeline that pushes the image to Amazon ECR and rolls an Amazon ECS service (off by default, see demo mode below).

> Note: This is a sample/reference project. It is not actively deployed. `ci.yml` runs on every push and pull request; the two AWS pipelines run manually and in demo mode (see [CI/CD demo mode](#cicd-demo-mode)).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/deploy-pipeline-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/deploy-pipeline-light.svg">
  <img width="880" src="assets/diagrams/deploy-pipeline-light.svg" alt="The deploy.yml pipeline. A developer runs the workflow by hand and the test job runs pytest against MongoDB 8.2 with an 80% coverage gate. By default the demo job runs and the deploy is skipped. With DEPLOY_ENABLED=true the deploy job, in the production environment, logs in to AWS with GitHub OIDC by assuming the IAM deploy role, builds the Docker image tagged with the commit SHA and pushes it to Amazon ECR, renders the task definition, deploys it to the Amazon ECS Fargate service and waits for a steady state, then smoke tests /health. ECS pulls the image from ECR. Dashed lines and boxes are disabled until DEPLOY_ENABLED=true, and the AWS side is set up by hand from aws/README.md.">
</picture>

The spec behind the picture is [`assets/diagrams/deploy-pipeline.yaml`](assets/diagrams/deploy-pipeline.yaml), rendered with [orrery](https://github.com/Sagargupta16/orrery).

![User management on desktop](assets/screenshots/users-desktop.png)

| Blogs on desktop | Users on a phone | Blogs on a phone |
| --- | --- | --- |
| ![Blog management on desktop](assets/screenshots/blogs-desktop.png) | ![User management at 390px](assets/screenshots/users-phone.png) | ![Blog management at 390px](assets/screenshots/blogs-phone.png) |

Captured from a local run with the demo data from `scripts/seed.py` (see [Screenshots](#screenshots)).

## Quick Start

One command, no cloud account needed:

```bash
git clone https://github.com/Sagargupta16/DevOps-AWS-FARM.git
cd DevOps-AWS-FARM
docker compose up --build
```

This starts MongoDB 8.2, runs the test suite against it with an 80% coverage gate, and starts the app on `http://localhost:8000` only after the tests pass. `docker compose ps` shows the app as `healthy` once `/health` answers. To use MongoDB Atlas instead, pass the connection string:

```bash
MONGODB_URL="mongodb+srv://<user>:<password>@<cluster>.mongodb.net/blogging" docker compose up --build
```

Load demo users and posts (standard library only, safe to re-run):

```bash
python scripts/seed.py
```

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [CI/CD Pipelines](#cicd-pipelines)
- [Tech Decisions](#tech-decisions)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Overview

DevOps-AWS-FARM is a small user and blog CRUD app whose real subject is the delivery pipeline around it. The React client is built by Vite and served by FastAPI from the same container, so one image covers the whole app and one ECS service runs it. Every push runs `ci.yml` (lint, tests, client build). The manually dispatched AWS pipelines lay out the rest of the path to a stable ECS service: a MongoDB service container for integration tests, keyless AWS access through GitHub OIDC, a SHA-tagged image in ECR, and an ECS rollout that waits for the service to stabilise.

## Features

- **FastAPI backend**: user and blog CRUD with automatic OpenAPI docs at `/docs`
- **React 19 frontend**: tabbed user and blog management UI, responsive down to phone widths
- **MongoDB**: document storage through PyMongo, MongoDB 8.2 in Docker or MongoDB Atlas
- **Password hashing**: bcrypt; password hashes are never returned by the API
- **Unique emails**: a unique index plus a pre-check; a taken email returns 409 on create and update
- **Health check**: `GET /health` pings MongoDB and returns 200 or 503; the Docker, ECS and ALB health checks all use it
- **Structured logs**: one JSON object per line in the container (`LOG_FORMAT=json`), with method, path, status and duration for every request
- **Docker**: multi-stage image (Node builds the client, Python serves API and client), hash-locked wheels only, runs as a non-root user
- **Docker Compose**: MongoDB, a test container with a coverage gate, then the app
- **Tests**: 31 HTTP-level pytest tests against a real MongoDB, 80% coverage gate in CI
- **Code quality**: flake8 in CI; black, ESLint, stylelint, Prettier and SonarQube in the full pipeline
- **CI/CD**: GitHub Actions workflows for lint, test, build, ECR publish and ECS deploy, with OIDC instead of stored AWS keys

## Architecture

### Application

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/diagrams/application-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/diagrams/application-light.svg">
  <img width="880" src="assets/diagrams/application-light.svg" alt="The application. A browser requests /, /user and /blog, and the Docker, ECS and ALB health checks request /health, from FastAPI and Uvicorn on port 8000 inside one Docker image (python:3.14-slim, non-root). FastAPI serves the React 19 build from client_build/, built by Vite, and hands API calls to routes/ (HTTP and the Pydantic v2 models), which call services/ (Mongo queries and bcrypt), which reach MongoDB 8.2 or Atlas through MONGODB_URL.">
</picture>

The spec behind the picture is [`assets/diagrams/application.yaml`](assets/diagrams/application.yaml), rendered with [orrery](https://github.com/Sagargupta16/orrery).

The MongoDB connection is resolved in this order: the `MONGODB_URL` environment variable, then `config/secrets.yml`, then `mongodb://localhost:27017/blogging`.

### AWS deployment

[The pipeline figure at the top](#devops-aws-farm) is `deploy.yml`. It never runs on push. With `DEPLOY_ENABLED` unset it stops after the tests; set it and the AWS variables from [aws/README.md](aws/README.md) and the same run deploys.

## CI/CD Pipelines

| Workflow | Trigger | What it does | Blocking |
| --- | --- | --- | --- |
| [`ci.yml`](.github/workflows/ci.yml) | push and PR to `main`, manual | flake8; pytest against a MongoDB 8.2 service container with `--cov-fail-under=80`; Vite production build | yes |
| [`deploy.yml`](.github/workflows/deploy.yml) | manual | pytest with MongoDB, then OIDC login, docker build, ECR push tagged with the commit SHA, task definition render, ECS deploy that waits for stability, `/health` smoke test | tests yes, deploy gated by `DEPLOY_ENABLED` and the `production` environment |
| [`main.yml`](.github/workflows/main.yml) | manual | black check (opens an auto-format PR when enabled), flake8, ESLint, stylelint, Prettier, coverage report, SonarQube scan, then a versioned ECR publish and ECS task-definition deploy | quality steps non-blocking, publish gated by `DEPLOY_ENABLED` |

### CI/CD demo mode

The two AWS pipelines run in demo mode. They show the full flow without touching a live AWS account:

- Deploy and publish jobs are skipped unless the repository variable `DEPLOY_ENABLED` is `true`.
- `deploy.yml` holds the live deploy steps. `main.yml` keeps its release and ECR/ECS steps commented out (kept visible for reference).
- `main.yml` quality gates (pytest coverage, ESLint, stylelint, SonarQube) still run but are non-blocking. The test job in `deploy.yml` is blocking.
- `ci.yml` is not in demo mode: its lint, test and build jobs must pass.
- To deploy for real: create the AWS resources and repo variables in [aws/README.md](aws/README.md), then set `DEPLOY_ENABLED=true`.

## Tech Decisions

- **One image for API and client.** The Dockerfile builds the React app in a `node:22-alpine` stage and copies the output into the Python image, where FastAPI serves it at `/`. One ECS service, one origin, no CORS setup.
- **Same-origin in development too.** The Vite dev server proxies `/user`, `/blog` and `/health` to `localhost:8000`, so the client never calls the API cross-origin.
- **No AWS keys in GitHub.** The deploy job asks GitHub for an OIDC token and assumes an IAM role whose trust policy accepts only this repo's `production` environment ([aws/github-oidc-trust-policy.json](aws/github-oidc-trust-policy.json)). Credentials last for the run; there is nothing to rotate or leak.
- **Images named by commit.** Every image is tagged with the commit SHA in an immutable ECR repository, and the task definition is rendered from the latest registered revision with only the image swapped. A re-run of the same commit reuses the image it already pushed.
- **A health check that means something.** `/health` returns 200 only when MongoDB answers a ping within 2 seconds, else 503. A task that cannot reach its database fails the container and ALB checks and is replaced, and the ECS circuit breaker rolls back a rollout whose tasks never get healthy.
- **Hash-locked, wheels-only installs.** CI, the deploy pipeline and both Dockerfiles install `requirements.lock.txt` with `--require-hashes --only-binary :all:`, so no package runs a build script and nothing unpinned gets in. The image moved from alpine to slim because pymongo ships no musllinux wheel; alpine had to keep gcc around to compile it. npm installs use the lockfile with `--ignore-scripts`.
- **Secrets stay out of git and the image.** `config/secrets.yml` is listed in both `.gitignore` and `.dockerignore`. In containers the connection string comes from `MONGODB_URL` (an ECS task-definition secret or environment variable in AWS), and the app logs only the MongoDB host.
- **bcrypt called directly.** passlib is unmaintained and fails on bcrypt 5, so the app hashes with `bcrypt` itself. Passwords longer than 72 bytes, which bcrypt cannot hash, are rejected with a 422.
- **Integration tests against a real database.** The tests drive the app over HTTP with FastAPI's `TestClient` against a MongoDB service container rather than mocks, so status codes, validation and the Mongo queries are all exercised. Test documents carry a per-run marker and only those are deleted afterwards, so the suite is safe to point at a shared database.
- **Gated deploys.** In `deploy.yml` the deploy job `needs` the blocking test job, runs only when `DEPLOY_ENABLED` is `true`, waits on the `production` environment, and is green only after ECS reports a steady state.
- **Dependency updates.** Renovate (shared preset) groups updates into monthly PRs (minor/patch and major kept separate) that auto-merge on green CI; security fixes skip the schedule.

## Getting Started

### Prerequisites

- **Python 3.11+** (3.14 in the image and CI)
- **Node.js 20.19+ or 22.12+** and **npm** (Vite 8 requirement)
- **MongoDB** (local, Docker or Atlas)
- **Docker** with **Docker Compose** (for the containerized setup)
- **Git**

### Local Development Setup

#### 1. Clone the repository

```bash
git clone https://github.com/Sagargupta16/DevOps-AWS-FARM.git
cd DevOps-AWS-FARM
```

#### 2. Backend setup

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

Install the Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure MongoDB

Either export `MONGODB_URL`, or use the secrets file:

1. Copy the secrets template:
   ```bash
   cp config/secrets.yml.example config/secrets.yml
   ```

2. Update `config/secrets.yml` with your MongoDB Atlas credentials:
   ```yaml
   mongodb:
     host: your-cluster.mongodb.net
     port: 27017
     username: your-username
     password: your-password
     database: mongodb+srv://your-username:your-password@your-cluster.mongodb.net/your-database-name
   ```

3. Get MongoDB Atlas credentials:
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Create a cluster or use an existing one
   - Go to Database Access and create a database user
   - Go to Network Access and allow your IP (or 0.0.0.0/0 for development)
   - Click "Connect" on your cluster and choose "Connect your application"
   - Copy the connection string and update the values in `secrets.yml`

With neither set, the app falls back to `mongodb://localhost:27017/blogging`.

**Note:** `config/secrets.yml` is ignored by git and excluded from the Docker build context. Never commit database credentials.

#### 4. Frontend setup

```bash
cd client
npm install
npm run build
```

This writes the production bundle to `../client_build`, which the FastAPI server serves at `/`. Without it the server still starts and serves the API only, with a warning in the log.

## Running the Application

### Development mode

Backend (from the project root, virtual environment active):

```bash
uvicorn main:app --reload --port 8000
```

Frontend dev server with hot reload:

```bash
cd client
npm run dev
```

This serves the React app on `http://localhost:3000` and proxies `/user`, `/blog` and `/health` to the backend on port 8000.

Logs are plain text locally. Set `LOG_FORMAT=json` to get the same one-object-per-line output the container writes:

```json
{"ts": "2026-10-18T11:44:31.007+00:00", "level": "INFO", "logger": "config.logging", "message": "request", "method": "POST", "path": "/user", "status": 409, "duration_ms": 3.32}
```

### Production mode with Docker

```bash
# Build and run in the background
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Testing

The tests need a reachable MongoDB (`MONGODB_URL`, or `localhost:27017`). They go through the real app over HTTP: CRUD happy paths, 404 for unknown ids, 422 for bad bodies and over-long passwords, 409 for duplicate emails (including the race the unique index catches), `/health` up and down, and the JSON log fields. The run on 2026-10-18 against MongoDB 8.2: 31 passed, 94.74% coverage.

```bash
# Run all tests
pytest

# What CI enforces
pytest tests/ --cov=. --cov-fail-under=80

# HTML coverage report
coverage run -m pytest
coverage html
```

In Docker, against the Compose MongoDB:

```bash
docker compose run --rm tests
```

## API Documentation

With the server running:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI schema**: `http://localhost:8000/openapi.json`

### Endpoints

| Method | Path | Success | Notes |
| --- | --- | --- | --- |
| `GET` | `/health` | 200 | `{"status": "ok", "database": "up"}`; 503 with `"database": "down"` when MongoDB does not answer a ping within 2 seconds |
| `POST` | `/user` | 201 | Creates a user, returns `{message, id}`; password stored as a bcrypt hash; 409 if the email is taken; 422 if the password is over 72 bytes |
| `GET` | `/user` | 200 | Lists users (empty list when there are none); hashes are not returned |
| `GET` | `/user/{user_id}` | 200 | 404 if not found |
| `PUT` | `/user/{user_id}` | 200 | Replaces name, email and password; returns the id; 404 if not found; 409 if the email belongs to another user |
| `DELETE` | `/user/{user_id}` | 202 | 404 if not found |
| `POST` | `/blog` | 201 | Creates a post, returns `{message, id}` |
| `GET` | `/blog` | 200 | Lists posts (empty list when there are none) |
| `GET` | `/blog/{blog_id}` | 200 | 404 if not found |
| `PUT` | `/blog/{blog_id}` | 200 | Returns the updated post; 404 if not found |
| `DELETE` | `/blog/{blog_id}` | 204 | 404 if not found |
| `GET` | `/` | 200 | Serves the React app |

User records are plain CRUD: there is no login or token endpoint.

![Swagger UI at /docs](assets/screenshots/api-docs-desktop.png)

## Screenshots

The images in this README come from [`client/scripts/screenshots.mjs`](client/scripts/screenshots.mjs) (Playwright, Chromium) at 1440x900 and 390x844. To regenerate them against a running app:

```bash
python scripts/seed.py
cd client
npm run screenshots   # BASE_URL=http://localhost:3000 to shoot the Vite dev server instead
```

The first run needs a browser: `npx playwright install chromium`.

## Deployment

### AWS deployment with GitHub Actions

Flow: **Docker image -> Amazon ECR -> Amazon ECS**. Both AWS workflows are started manually (`workflow_dispatch`) and stay in demo mode until enabled.

The deploy job in `deploy.yml`, trimmed to the steps that matter:

```yaml
deploy:
  needs: test                                   # blocking pytest job with a MongoDB service container
  if: ${{ vars.DEPLOY_ENABLED == 'true' }}
  environment: production                       # add required reviewers to gate on an approval
  permissions:
    contents: read
    id-token: write                             # OIDC: no AWS keys stored in GitHub
  steps:
    - uses: aws-actions/configure-aws-credentials@<sha>  # v6.3.0
      with:
        role-to-assume: ${{ vars.AWS_ROLE_ARN }}
    - uses: aws-actions/amazon-ecr-login@<sha>  # v2.1.7
    - run: |                                    # $IMAGE ends in :${{ github.sha }}
        docker build --tag "$IMAGE" .
        docker push "$IMAGE"
    - uses: aws-actions/amazon-ecs-render-task-definition@<sha>  # v1.9.1
      with:
        task-definition-family: ${{ vars.ECS_TASK_FAMILY }}
    - uses: aws-actions/amazon-ecs-deploy-task-definition@<sha>  # v2.6.4
      with:
        wait-for-service-stability: true
    - run: curl --fail "$APP_URL/health"
```

The image does not contain `config/secrets.yml`; the task definition injects `MONGODB_URL` from Secrets Manager.

#### AWS resources and repo variables

[aws/README.md](aws/README.md) has the one-time setup and teardown commands, plus the three templates the pipeline expects:

- [`github-oidc-trust-policy.json`](aws/github-oidc-trust-policy.json): who may assume the deploy role (this repo, `production` environment only)
- [`deploy-role-policy.json`](aws/deploy-role-policy.json): what the role may do (push to one ECR repository, update one ECS service, pass the task roles to ECS)
- [`task-definition.json`](aws/task-definition.json): the Fargate task, with the `/health` container check and JSON logs to CloudWatch

Repository variables (not secrets; none of them is sensitive):

```
AWS_ROLE_ARN        # deploy role assumed through OIDC
AWS_REGION          # e.g. us-east-1
ECR_REPOSITORY      # repository name, e.g. devops-aws-farm
ECS_CLUSTER         # cluster name
ECS_SERVICE         # service name
ECS_TASK_FAMILY     # task definition family
ECS_CONTAINER_NAME  # container in the task definition, e.g. app
APP_URL             # optional: public URL for the /health smoke test
DEPLOY_ENABLED      # true to deploy
```

#### Manual deployment commands

```bash
# 1. Build and tag the image with the commit (the ECR repository uses immutable tags)
TAG=$(git rev-parse HEAD)
docker build -t your-account.dkr.ecr.us-east-1.amazonaws.com/devops-aws-farm:$TAG .

# 2. Log in to ECR and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/devops-aws-farm:$TAG

# 3. Point `image` in aws/task-definition.json at the new tag, register the revision and roll the service onto it
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json
aws ecs update-service --cluster devops-aws-farm --service devops-aws-farm --task-definition devops-aws-farm
```

The pipeline does all three steps for you.

## Project Structure

```
DevOps-AWS-FARM/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Lint, test (MongoDB service), client build on every push/PR
│       ├── deploy.yml      # Manual: test -> OIDC -> ECR push -> ECS deploy (demo mode)
│       └── main.yml        # Manual: full quality pipeline -> ECR publish -> ECS (demo mode)
├── assets/diagrams/        # README diagrams: orrery specs and the SVGs rendered from them
├── assets/screenshots/     # README screenshots (generated by client/scripts/screenshots.mjs)
├── aws/                    # OIDC trust policy, deploy role policy, task definition, setup guide
├── client/                 # React 19 + Vite frontend
│   ├── src/                # App.jsx, main.jsx, styles
│   ├── scripts/            # screenshots.mjs (Playwright)
│   ├── public/             # Static assets
│   ├── vite.config.js      # Build output to ../client_build, dev proxy to :8000
│   └── package.json
├── client_build/           # Built React app (generated, gitignored)
├── config/
│   ├── secrets.yml.example # Template for MongoDB credentials
│   ├── secrets_parser.py   # Resolves the MongoDB connection
│   ├── logging.py          # Logging setup from logging.yml (LOG_FORMAT=json switches formatter)
│   ├── json_formatter.py   # One JSON object per log line
│   └── logging.yml
├── models/                 # Pydantic models (blog, user)
├── routes/                 # FastAPI routers (blog, user, health)
├── scripts/
│   └── seed.py             # Demo users and posts through the API
├── services/               # MongoDB operations (blog, user)
├── tests/                  # pytest suite (HTTP-level, real MongoDB)
├── utils/
│   └── hashing.py          # bcrypt password hashing
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── requirements.lock.txt   # Hash-locked pins CI and the images install (generated from requirements.txt)
├── Dockerfile              # Multi-stage app image
├── Dockerfile.tests        # Test runner image with coverage gate
├── docker-compose.yml      # MongoDB + tests + app
└── README.md
```

## Technologies

### Backend

- **FastAPI**: Python web framework with OpenAPI docs
- **Uvicorn**: ASGI server
- **Pydantic v2**: request and response validation
- **PyMongo**: MongoDB driver
- **bcrypt**: password hashing
- **PyYAML**: YAML config and logging setup

### Frontend

- **React 19**
- **Vite 8**: build tool and dev server
- **Axios**: HTTP client

### Testing and quality

- **pytest** and **pytest-cov / coverage**: tests and the 80% coverage gate
- **flake8**: Python linting (blocking in CI)
- **Playwright**: README screenshots
- **black**, **ESLint**, **stylelint**, **Prettier**, **SonarQube**: run in the manual `main.yml` pipeline

### DevOps and deployment

- **Docker** and **Docker Compose**
- **GitHub Actions** with OIDC federation to AWS
- **Amazon ECR**, **Amazon ECS on Fargate**, **Secrets Manager**, **CloudWatch Logs**
- **Renovate**: grouped monthly dependency updates

### Database

- **MongoDB 8.2** (Docker) or **MongoDB Atlas**

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run tests (`pytest`) and keep coverage above 80%
5. Run linting (`flake8`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Open a Pull Request

### Code Style

- Python: PEP 8, checked by flake8
- JavaScript: Prettier formatting
- All tests pass and coverage stays above 80%

## Troubleshooting

### Common Issues

1. **Port 8000 already in use:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -ti:8000 | xargs kill -9
   ```

2. **MongoDB connection issues:**
   - Ensure MongoDB is running
   - Check `MONGODB_URL` or the connection string in `config/secrets.yml`
   - Verify network accessibility (Atlas Network Access list)

3. **`/` returns 404 and the log says `client_build/ not found`:**
   - The API is up but the React build is missing. Build it from `client/`: `npm install`, then `npm run build`

4. **Dependency issues:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

### Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation and issues
- Review the API documentation at the `/docs` endpoint

## License

[MIT](LICENSE)
