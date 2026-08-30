# Local Development Guide

For contributors, enterprise engineers deploying BYOC (Bring Your Own Cloud), or users who want to poke around under the hood, this guide covers how to run the API Guardian stack locally on your workstation.

## Prerequisites
Before you begin, ensure you have the following installed:
- **Docker & Docker Compose:** The entire stack is containerized for portability.
- **Python 3.12+:** Required for running the control plane and workers locally if not using Docker.
- **Node.js 20+ & npm:** Required for building and running the Next.js frontend.
- **Git:** For version control.

## Bootstrapping the Environment
1. **Clone the Repository:** 
   `git clone https://github.com/prathik578/api-guardian.git`
2. **Environment Variables:**
   Copy the example file to create your local config.
   `cp .env.example .env`
   *Note: Ensure `DATABASE_URL` is set correctly for your local Postgres instance.*
3. **Start the Infrastructure:**
   Use Docker Compose to spin up the database and message queue.
   `docker compose up -d postgres redis squid-proxy`
4. **Database Migrations:**
   Initialize the PostgreSQL schema using Alembic.
   `DATABASE_URL="..." alembic upgrade head`

## Running the Services
You need to start two main processes:

### The Backend (FastAPI)
Navigate to the root directory and start the Uvicorn server:
`uvicorn api_guardian.api.app:app --reload --host 127.0.0.1 --port 8000`

### The Frontend (Next.js)
Navigate to the `frontend/` directory, install dependencies, and start the development server:
```bash
cd frontend
npm install
npm run dev
```

You can now access the dashboard at `http://localhost:3000`. Hot-reloading is enabled for both the frontend React components and the backend Python routes, allowing for a rapid and highly productive local development experience.
