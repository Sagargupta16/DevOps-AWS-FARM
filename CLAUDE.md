# CLAUDE.md

> This file stacks on top of the workspace root at `C:\Code\GitHub\`:
> - Root [`CLAUDE.md`](../../CLAUDE.md) -- voice, rules, routing map, references, skills, slash commands, conventions.
> - Root [`MEMORY.md`](../../MEMORY.md) -- live facts across repos.
> - Root [`STATUS.md`](../../STATUS.md) -- live PR/CI/security dashboard.
> - [`.claude/resources/`](../../.claude/resources/README.md) -- deep reference for collaboration, workflow, git, OSS, debugging, voice.
>
> Read those first. The guidance below only adds **repo-specific context** -- it does not override anything in the root.

## Project

FARM-stack (FastAPI + React + MongoDB) demo app with user and blog CRUD, built to showcase a DevOps pipeline: Docker image -> ECR -> ECS via GitHub Actions.

## Stack

- **Language**: Python 3.11+ (backend), JavaScript (frontend)
- **Framework**: FastAPI + Uvicorn; React 19 via Create React App (react-scripts)
- **Database**: MongoDB Atlas (PyMongo)
- **Package manager**: pip (`requirements.txt`), npm (`client/package.json`)
- **Deploy target**: AWS ECS (image in ECR), pushed on merge to main by GitHub Actions

## Run

```
pip install -r requirements.txt
cd client && npm install && npm run build   # produces ../client_build
uvicorn main:app --reload --port 8000
```

Or all-in-one: `docker-compose up --build` (runs tests container first, then app on port 8000).

Frontend dev server: `cd client && npm start` (port 3000, proxies API to localhost:8000).

## Test

```
pytest                                    # plain run
pytest tests/ --cov=. --cov-fail-under=80 # what CI enforces
```

## Entry points

- `main.py` -- FastAPI app; includes blog/user routers, mounts `client_build/` as static frontend at `/`
- `client/src/` -- React frontend source (CRA)

## Key files

- `routes/` -> `services/` -> `models/` -- API layering (blog + user in each)
- `config/secrets_parser.py` -- resolves the Mongo connection (`MONGODB_URL` env var first, else `config/secrets.yml`)
- `config/secrets.yml.example` -- template; copy to `config/secrets.yml` for Atlas credentials
- `.github/workflows/deploy.yml` -- test (Mongo service container) -> build -> ECR push -> ECS deploy

## Gotchas

- `uvicorn main:app` crashes at import if `client_build/` is missing -- build the client first. `npm run build` in `client/` moves CRA's `build/` output to `../client_build` itself.
- Mongo connection resolves in order: `MONGODB_URL` env var -> `config/secrets.yml` (gitignored) -> `mongodb://localhost:27017/blogging` fallback. The parser warns on a missing secrets file but never fails.
- CI hard-gates deploy on 80% pytest coverage.
- Workflow labels drift from reality: steps named "Set up Python 3.11" actually install 3.14; `main.yml` still carries a stale `BRANCH_NAME: master` env var.
- Local `.env` and `config/secrets.yml` exist on disk but are gitignored and untracked -- keep it that way.

## Repo-specific rules

- Uses pip + requirements.txt and npm (not uv/pnpm) -- predates the workspace defaults; keep as-is unless migrating deliberately.

## API routes

- `/user`, `/user/{user_id}` -- user CRUD (passwords bcrypt-hashed via passlib); no login/token endpoint
- `/blog`, `/blog/{blog_id}` -- blog post CRUD
- OpenAPI at `/docs` when the server is running.
