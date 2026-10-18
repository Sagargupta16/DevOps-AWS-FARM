# DevOps-AWS-FARM

[![CI](https://github.com/Sagargupta16/DevOps-AWS-FARM/actions/workflows/ci.yml/badge.svg)](https://github.com/Sagargupta16/DevOps-AWS-FARM/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A FARM-stack app (FastAPI, React 19, MongoDB) packaged as a single Docker image, with GitHub Actions pipelines: lint, test and build on every push and pull request, plus a manually dispatched pipeline that pushes the image to Amazon ECR and rolls an Amazon ECS service (off by default, see demo mode below).

> Note: This is a sample/reference project. It is not actively deployed. `ci.yml` runs on every push and pull request; the two AWS pipelines run manually and in demo mode (see [CI/CD demo mode](#cicd-demo-mode)).

## Quick Start

One command, no cloud account needed:

```bash
git clone https://github.com/Sagargupta16/DevOps-AWS-FARM.git
cd DevOps-AWS-FARM
docker compose up --build
```

This starts MongoDB 8.2, runs the test suite against it with an 80% coverage gate, and starts the app on `http://localhost:8000` only after the tests pass. To use MongoDB Atlas instead, pass the connection string:

```bash
MONGODB_URL="mongodb+srv://<user>:<password>@<cluster>.mongodb.net/blogging" docker compose up --build
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
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Overview

DevOps-AWS-FARM is a small user and blog CRUD app whose real subject is the delivery pipeline around it. The React client is built by Vite and served by FastAPI from the same container, so one image covers the whole app and one ECS service runs it. Every push runs `ci.yml` (lint, tests, client build). The manually dispatched AWS pipelines lay out the rest of the path to a stable ECS service: quality gates, a MongoDB service container for integration tests, image build, ECR push and an ECS rolling deploy that waits for `services-stable`.

## Features

- **FastAPI backend**: user and blog CRUD with automatic OpenAPI docs at `/docs`
- **React 19 frontend**: tabbed user and blog management UI, responsive down to phone widths
- **MongoDB**: document storage through PyMongo, MongoDB 8.2 in Docker or MongoDB Atlas
- **Password hashing**: bcrypt; password hashes are never returned by the API
- **Docker**: multi-stage image (Node builds the client, Python serves API and client)
- **Docker Compose**: MongoDB, a test container with a coverage gate, then the app
- **Tests**: pytest suite run against a real MongoDB, 80% coverage gate in CI
- **Code quality**: flake8 in CI; black, ESLint, stylelint, Prettier and SonarQube in the full pipeline
- **CI/CD**: GitHub Actions workflows for lint, test, build, ECR publish and ECS deploy

## Architecture

### Application

```mermaid
flowchart LR
    browser["Browser"] -->|"GET / (static React build)"| app
    browser -->|"JSON: /user, /blog"| app
    subgraph image["Docker image (python:3.14-alpine)"]
        app["FastAPI + Uvicorn :8000"]
        routes["routes/ (HTTP, response models)"]
        services["services/ (Mongo queries, bcrypt)"]
        models["models/ (Pydantic v2 validation)"]
        static["client_build/ (Vite output)"]
        app --> routes --> services
        routes -.-> models
        app --> static
    end
    services --> mongo[("MongoDB 8.2 or Atlas")]
```

The MongoDB connection is resolved in this order: the `MONGODB_URL` environment variable, then `config/secrets.yml`, then `mongodb://localhost:27017/blogging`.

### AWS deployment

```mermaid
flowchart LR
    dev["manual run (workflow_dispatch)"] --> test["test job: pytest + MongoDB service"]
    test --> flag{"DEPLOY_ENABLED = true?"}
    flag -->|"no (default)"| demo["demo job: deploy skipped"]
    flag -->|"yes"| build["docker build"]
    build -->|"tag :sha and :latest"| ecr[("Amazon ECR")]
    ecr -->|"update-service --force-new-deployment"| ecs["Amazon ECS service"]
    ecs -->|"wait services-stable"| live["new tasks running"]
```

This is `deploy.yml`. It never runs on push, and the ECR and ECS steps stay commented out until you enable them (see [CI/CD demo mode](#cicd-demo-mode)).

## CI/CD Pipelines

| Workflow | Trigger | What it does | Blocking |
| --- | --- | --- | --- |
| [`ci.yml`](.github/workflows/ci.yml) | push and PR to `main`, manual | flake8; pytest against a MongoDB 8.2 service container with `--cov-fail-under=80`; Vite production build | yes |
| [`deploy.yml`](.github/workflows/deploy.yml) | manual | pytest with MongoDB, then docker build, ECR push, `aws ecs update-service` and `aws ecs wait services-stable` | tests non-blocking, deploy gated by `DEPLOY_ENABLED` |
| [`main.yml`](.github/workflows/main.yml) | manual | black check (opens an auto-format PR when enabled), flake8, ESLint, stylelint, Prettier, coverage report, SonarQube scan, then a versioned ECR publish and ECS task-definition deploy | quality steps non-blocking, publish gated by `DEPLOY_ENABLED` |

### CI/CD demo mode

The two AWS pipelines run in demo mode. They show the full flow without touching a live AWS account:

- Deploy and publish jobs are skipped unless the repository variable `DEPLOY_ENABLED` is `true`, and the real ECR/ECS steps are commented out in the workflow files (kept visible for reference).
- Their quality gates (pytest coverage, ESLint, stylelint, SonarQube) still run but are non-blocking.
- `ci.yml` is not in demo mode: its lint, test and build jobs must pass.
- To deploy for real: set `DEPLOY_ENABLED=true`, add the secrets listed under [Required GitHub Secrets](#required-github-secrets), and uncomment the AWS steps in `deploy.yml` or `main.yml`.

## Tech Decisions

- **One image for API and client.** The Dockerfile builds the React app in a `node:22-alpine` stage and copies the output into the Python image, where FastAPI serves it at `/`. One ECS service, one origin, no CORS setup.
- **Same-origin in development too.** The Vite dev server proxies `/user` and `/blog` to `localhost:8000`, so the client never calls the API cross-origin.
- **Secrets stay out of git and the image.** `config/secrets.yml` is listed in both `.gitignore` and `.dockerignore`. In containers the connection string comes from `MONGODB_URL` (an ECS task-definition secret or environment variable in AWS), and the app logs only the MongoDB host.
- **bcrypt called directly.** passlib is unmaintained and fails on bcrypt 5, so the app hashes with `bcrypt` itself. Passwords longer than 72 bytes, which bcrypt cannot hash, are rejected with a 422.
- **Integration tests against a real database.** The tests call the route functions against a MongoDB service container rather than mocks, so the Mongo queries themselves are exercised.
- **Gated deploys.** In `deploy.yml` the deploy job `needs` the test job and only runs when `DEPLOY_ENABLED` is `true`, and the ECS step waits for `services-stable` before the run is green. In demo mode the test step is `continue-on-error`, so remove that line too when you turn deploys on.
- **Dependency updates.** Renovate (shared preset) groups updates into monthly PRs (minor/patch and major kept separate) that auto-merge on green CI; security fixes skip the schedule.

## Getting Started

### Prerequisites

- **Python 3.11+**
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

This writes the production bundle to `../client_build`, which the FastAPI server serves. The server will not start without it.

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

This serves the React app on `http://localhost:3000` and proxies `/user` and `/blog` to the backend on port 8000.

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

The tests need a reachable MongoDB (`MONGODB_URL`, or `localhost:27017`).

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
| `POST` | `/user` | 201 | Creates a user, returns `{message, id}`; password stored as a bcrypt hash |
| `GET` | `/user` | 200 | Lists users (empty list when there are none); hashes are not returned |
| `GET` | `/user/{user_id}` | 200 | 404 if not found |
| `PUT` | `/user/{user_id}` | 200 | Replaces name, email and password; returns the id; 404 if not found |
| `DELETE` | `/user/{user_id}` | 202 | 404 if not found |
| `POST` | `/blog` | 201 | Creates a post, returns `{message, id}` |
| `GET` | `/blog` | 200 | Lists posts (empty list when there are none) |
| `GET` | `/blog/{blog_id}` | 200 | 404 if not found |
| `PUT` | `/blog/{blog_id}` | 200 | Returns the updated post; 404 if not found |
| `DELETE` | `/blog/{blog_id}` | 204 | 404 if not found |
| `GET` | `/` | 200 | Serves the React app |

User records are plain CRUD: there is no login or token endpoint.

## Deployment

### AWS deployment with GitHub Actions

Flow: **Docker image -> Amazon ECR -> Amazon ECS**. Both AWS workflows are started manually (`workflow_dispatch`) and stay in demo mode until enabled.

The `deploy.yml` pipeline, once its AWS steps are uncommented:

```yaml
# 1. Run tests first (MongoDB service container)
- name: Run tests with coverage
  run: python -m pytest tests/ --cov=. --cov-report=xml --cov-fail-under=80

# 2. Build the image (deploy job needs the test job)
- name: Build Docker image
  run: docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .

# 3. Push to Amazon ECR
- name: Push image to Amazon ECR
  run: docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

# 4. Roll the ECS service and wait for it to settle
- name: Deploy to Amazon ECS
  run: |
    aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment
    aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE
```

The image does not contain `config/secrets.yml`, so set `MONGODB_URL` in the ECS task definition (ideally as a Secrets Manager reference).

#### Required GitHub Secrets

```
AWS_ACCESS_KEY_ID          # AWS access key
AWS_SECRET_ACCESS_KEY      # AWS secret key
AWS_REGION                 # AWS region (e.g., us-east-1)
ECR_REPOSITORY_URI         # ECR repository URI
ECS_CLUSTER_NAME           # ECS cluster name
ECS_SERVICE_NAME           # ECS service name
```

For a real account, prefer GitHub OIDC over long-lived keys: grant the job `id-token: write` and pass `role-to-assume` to `aws-actions/configure-aws-credentials` instead of the two key secrets.

#### Manual deployment commands

```bash
# 1. Build and tag the image
docker build -t devops-aws-farm .
docker tag devops-aws-farm:latest your-account.dkr.ecr.us-east-1.amazonaws.com/devops-aws-farm:latest

# 2. Log in to ECR and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/devops-aws-farm:latest

# 3. Roll the ECS service
aws ecs update-service --cluster your-cluster --service your-service --force-new-deployment
```

## Project Structure

```
DevOps-AWS-FARM/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Lint, test (MongoDB service), client build on every push/PR
│       ├── deploy.yml      # Manual: test -> ECR push -> ECS deploy (demo mode)
│       └── main.yml        # Manual: full quality pipeline -> ECR publish -> ECS (demo mode)
├── client/                 # React 19 + Vite frontend
│   ├── src/                # App.jsx, main.jsx, styles
│   ├── public/             # Static assets
│   ├── vite.config.js      # Build output to ../client_build, dev proxy to :8000
│   └── package.json
├── client_build/           # Built React app (generated, gitignored)
├── config/
│   ├── secrets.yml.example # Template for MongoDB credentials
│   ├── secrets_parser.py   # Resolves the MongoDB connection
│   ├── logging.py          # Logging setup from logging.yml
│   └── logging.yml
├── models/                 # Pydantic models (blog, user)
├── routes/                 # FastAPI routers (blog, user)
├── services/               # MongoDB operations (blog, user)
├── tests/                  # pytest suite
├── utils/
│   └── hashing.py          # bcrypt password hashing
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
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
- **black**, **ESLint**, **stylelint**, **Prettier**, **SonarQube**: run in the manual `main.yml` pipeline

### DevOps and deployment
- **Docker** and **Docker Compose**
- **GitHub Actions**
- **Amazon ECR** and **Amazon ECS**
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

3. **`RuntimeError: Directory 'client_build' does not exist`:**
   - Build the client first: `cd client && npm install && npm run build`

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
