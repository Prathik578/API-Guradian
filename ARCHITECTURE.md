# Architecture

API Guardian is composed of an event-driven, multi-tenant architecture designed for massive scale and deterministic reliability.

## Core Components
1. **Frontend (Next.js)**: A dynamic, app-router based React dashboard interacting exclusively with the API.
2. **API Backend (FastAPI)**: A high-performance Python backend serving the frontend and handling synchronous integrations, authentication, and platform logic.
3. **Database (PostgreSQL)**: The persistent storage layer enforcing multi-tenancy at the data tier utilizing Row-Level Security (RLS) to prevent cross-tenant data leaks.
4. **Task Workers (Celery)**: Background processors responsible for asynchronous tasks such as monitoring, migration, verification, and external provider synchronization.
5. **Sandbox (AWS Fargate)**: Secure, ephemeral execution environments designed for executing untrusted customer code during patch verification to prevent host compromise.
6. **Outbox Manager**: Transactional outbox implementation ensuring reliable event dispatch from the synchronous API to asynchronous workers.

## Workflow Overview
1. Sync APIs -> 2. Detect Change -> 3. Generate Patch (LLM) -> 4. Execute Sandbox Tests -> 5. Cryptographically sign evidence -> 6. Open GitHub PR.
