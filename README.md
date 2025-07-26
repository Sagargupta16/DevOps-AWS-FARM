# DevOps-AWS-FARM

A full-stack web application built with FastAPI, React, and MongoDB, containerized with Docker and deployed on AWS.

## 🚀 Quick Start

**⚠️ IMPORTANT: Before running the application, you MUST configure your database connection:**

```bash
# 1. Copy the secrets template
cp config/secrets.yml.example config/secrets.yml

# 2. Edit config/secrets.yml with your MongoDB Atlas credentials
# 3. Then run the application
docker-compose up --build
```

For detailed setup instructions, see [Getting Started](#getting-started) below.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
  - [Docker Setup](#docker-setup)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Mode with Docker](#production-mode-with-docker)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Contributing](#contributing)

## Overview

DevOps-AWS-FARM is a modern full-stack web application that demonstrates DevOps best practices using the FARM stack (FastAPI, React, MongoDB). The application includes user and blog management features with a complete CI/CD pipeline for AWS deployment.

## Features

- **FastAPI Backend**: High-performance Python web framework with automatic API documentation
- **React Frontend**: Modern React-based user interface
- **MongoDB Integration**: NoSQL database for data persistence
- **User Management**: User registration, authentication, and profile management
- **Blog System**: Create, read, update, and delete blog posts
- **Docker Support**: Containerized application for consistent deployment
- **Test Coverage**: Comprehensive test suite with coverage reporting
- **Code Quality**: Linting and formatting tools (Pylint, Flake8, Prettier)
- **CI/CD Ready**: Docker Compose setup for easy deployment

## Architecture

### Application Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │───▶│  FastAPI Server │───▶│   MongoDB Atlas │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### AWS Deployment Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│   Amazon ECR    │───▶│   Amazon ECS    │
│  (Source Code)  │    │ (Docker Images) │    │  (Containers)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       ▲                       │
         │                       │                       │
         ▼                       │                       ▼
┌─────────────────┐              │              ┌─────────────────┐
│ GitHub Actions  │──────────────┘              │ Application     │
│    (CI/CD)      │                             │ Load Balancer   │
└─────────────────┘                             └─────────────────┘
```

### CI/CD Workflow Diagram

```
┌─────────────┐
│ Developer   │
│ Push Code   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   GitHub    │
│ Repository  │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   GitHub    │───▶│  Run Tests  │───▶│    Build    │
│   Actions   │    │  Coverage   │    │   Docker    │
│  Triggered  │    │    80%+     │    │    Image    │
└─────────────┘    └──────┬──────┘    └──────┬──────┘
                          │                  │
                          ▼                  ▼
                 ┌─────────────┐    ┌─────────────┐
                 │    Tests    │    │    Push     │
                 │   Failed?   │    │   to ECR    │
                 │    Stop     │    │             │
                 └─────────────┘    └──────┬──────┘
                                           │
                                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Health    │◀───│   Deploy    │◀───│   Update    │
│   Check     │    │   to ECS    │    │ ECS Service │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐
│ Application │
│    Live     │
│             │
└─────────────┘
```

### CI/CD Process Steps

1. **Code Push**: Developer pushes code to GitHub repository
2. **GitHub Actions Trigger**: Workflow automatically starts on push to main branch
3. **Run Tests**: Execute pytest with 80% coverage requirement
4. **Test Gate**: If tests fail, deployment stops here
5. **Build Docker Image**: Creates containerized version of the application (only if tests pass)
6. **Push to ECR**: Uploads Docker image to Amazon Elastic Container Registry
7. **Deploy to ECS**: Updates ECS service with new Docker image
8. **Health Check**: Verifies application is running correctly
9. **Go Live**: Application is accessible to users

## Getting Started

### Prerequisites

Before running this application, make sure you have the following installed:

- **Python 3.11+**
- **Node.js 16+** and **npm**
- **MongoDB** (local or cloud instance)
- **Docker** and **Docker Compose** (for containerized setup)
- **Git**

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Sagargupta16/DevOps-AWS-FARM.git
cd DevOps-AWS-FARM
```

#### 2. Backend Setup

**Create and activate Python virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

**Install Python dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Configure MongoDB Connection (IMPORTANT):**

⚠️ **Before running the application, you MUST configure your MongoDB connection:**

1. **Copy the secrets template:**
   ```bash
   cp config/secrets.yml.example config/secrets.yml
   ```

2. **Update `config/secrets.yml` with your MongoDB Atlas credentials:**
   ```yaml
   mongodb:
     host: your-cluster.mongodb.net
     port: 27017
     username: your-username
     password: your-password
     database: mongodb+srv://your-username:your-password@your-cluster.mongodb.net/your-database-name
   ```

3. **Get MongoDB Atlas credentials:**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Create a cluster or use existing one
   - Go to Database Access and create a database user
   - Go to Network Access and whitelist your IP (or 0.0.0.0/0 for development)
   - Click "Connect" on your cluster and choose "Connect your application"
   - Copy the connection string and update the values in `secrets.yml`

📝 **Note:** The `secrets.yml` file is ignored by git for security. Never commit database credentials to version control.

#### 3. Frontend Setup

**Navigate to client directory and install dependencies:**
```bash
cd client
npm install
```

**Build the React application:**
```bash
npm run build
```

This will create the `client_build` directory that the FastAPI server serves.

### Docker Setup

**⚠️ IMPORTANT: Configure secrets before running Docker!**

Before using Docker, make sure to configure your MongoDB connection:

```bash
# Copy the secrets template
cp config/secrets.yml.example config/secrets.yml
# Edit config/secrets.yml with your MongoDB Atlas credentials
```

For a quick setup using Docker:

```bash
# Build and run with Docker Compose
docker-compose up --build
```

This will:
- Build the application image
- Run tests with coverage requirements (80%+)
- Start the application on port 8000

## Running the Application

### Development Mode

#### Option 1: Using VS Code Task (Recommended)
If you're using VS Code, you can use the built-in task:
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select "Start FastAPI Development Server"

#### Option 2: Manual Command
```bash
# Make sure you're in the project root and virtual environment is activated
uvicorn main:app --reload --port 8000
```

#### Option 3: Frontend Development Server (for React development)
```bash
cd client
npm start
```
This runs React dev server on `http://localhost:3000`

### Production Mode with Docker

```bash
# Build and run the production container
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Testing

### Run Tests Locally
```bash
# Run all tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage report
coverage html  # Generate HTML coverage report
```

### Run Tests in Docker
```bash
# Tests are automatically run during Docker Compose build
docker-compose up tests
```

The application requires **80% test coverage** to pass the build process.

## API Documentation

Once the FastAPI server is running, you can access:

- **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative API Documentation (ReDoc)**: `http://localhost:8000/redoc`
- **OpenAPI JSON Schema**: `http://localhost:8000/openapi.json`

### Available Endpoints

- **User Routes**: `/users/*` - User management and authentication
- **Blog Routes**: `/blogs/*` - Blog post CRUD operations
- **Frontend**: `/` - Serves the React application

## Deployment

### AWS Deployment with GitHub Actions

The application automatically deploys to AWS when code is pushed to the main branch:

**Docker Image → ECR → ECS**

#### GitHub Actions Workflow

The `.github/workflows/deploy.yml` file contains the deployment pipeline:

```yaml
# 1. Run Tests First
- name: Run tests with coverage
  run: python -m pytest tests/ --cov=. --cov-report=xml --cov-fail-under=80

# 2. Build Docker Image (only if tests pass)
- name: Build Docker image
  run: docker build -t devops-aws-farm .

# 3. Push to Amazon ECR
- name: Push to ECR
  run: |
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    docker tag devops-aws-farm:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

# 4. Deploy to Amazon ECS
- name: Deploy to ECS
  run: |
    aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment
    aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE
```

#### Required GitHub Secrets

Add these secrets in your GitHub repository settings:

```
AWS_ACCESS_KEY_ID          # AWS access key
AWS_SECRET_ACCESS_KEY      # AWS secret key  
AWS_REGION                 # AWS region (e.g., us-east-1)
ECR_REPOSITORY_URI         # ECR repository URI
ECS_CLUSTER_NAME           # ECS cluster name
ECS_SERVICE_NAME           # ECS service name
```

#### Manual Deployment Commands

For manual deployment, use these commands:

```bash
# 1. Build and tag Docker image
docker build -t devops-aws-farm .
docker tag devops-aws-farm:latest your-account.dkr.ecr.us-east-1.amazonaws.com/devops-aws-farm:latest

# 2. Login to ECR and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/devops-aws-farm:latest

# 3. Update ECS service
aws ecs update-service --cluster your-cluster --service your-service --force-new-deployment
```

## Project Structure

```
DevOps-AWS-FARM/
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions CI/CD pipeline
├── client/                # React frontend application
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
├── client_build/          # Built React app (served by FastAPI)
├── config/                # Configuration files
│   ├── secrets.yml.example # Template for MongoDB credentials
│   ├── secrets.yml        # Your actual MongoDB credentials (git-ignored)
│   ├── logging.py         # Logging configuration
│   └── secrets_parser.py  # Configuration parser
├── models/                # Pydantic data models
│   ├── blog_models.py     # Blog-related models
│   └── user_models.py     # User-related models
├── routes/                # FastAPI route handlers
│   ├── blog_routes.py     # Blog API endpoints
│   └── user_routes.py     # User API endpoints
├── services/              # Business logic layer
│   ├── blog_services.py   # Blog operations
│   └── user_services.py   # User operations
├── tests/                 # Test suite
├── utils/                 # Utility functions
│   └── hashing.py         # Password hashing utilities
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Multi-container setup
└── README.md             # This file
```

## Technologies

### Backend
- **FastAPI**: Modern, high-performance Python web framework
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type annotations
- **PyMongo**: MongoDB driver for Python
- **Passlib & Bcrypt**: Password hashing and verification
- **PyYAML**: YAML configuration file support

### Frontend
- **React 19**: JavaScript library for building user interfaces
- **React Scripts**: Build tools and development server

### Testing & Quality
- **Pytest**: Testing framework
- **Coverage**: Code coverage measurement
- **Pylint**: Python code linting
- **Flake8**: Style guide enforcement
- **Prettier**: Code formatting for JavaScript
- **ESLint**: JavaScript/React linting

### DevOps & Deployment
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container orchestration
- **AWS ECR**: Container registry
- **GitHub Actions**: CI/CD pipeline (configurable)

### Database
- **MongoDB**: NoSQL document database

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run tests (`pytest`) and ensure coverage is above 80%
5. Run linting (`flake8` and `pylint`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

### Code Style
- Python: Follow PEP 8 guidelines
- JavaScript: Use Prettier for formatting
- Ensure all tests pass and maintain test coverage above 80%

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
   - Check connection string in `config/secrets.yml`
   - Verify network accessibility

3. **Dependencies issues:**
   ```bash
   # Update pip and reinstall requirements
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

### Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation and issues
- Review the API documentation at `/docs` endpoint
