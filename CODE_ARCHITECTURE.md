# API Guardian — Code & Repository Architecture

**Status:** Approved Structural Blueprint  
**Version:** 1.0  
**Date:** 2026-08-22  
**Companion Document:** [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 1. Purpose & Principles

This document defines the **physical code layout, file ownership, and package dependencies** for implementing API Guardian. It enforces the architectural invariants established in `ARCHITECTURE.md`.

### Core Architectural Style

- **Modular Monolith + Asynchronous Workers + Ephemeral Execution Plane.**
- Clean onion architecture within the core Python package (`src/api_guardian/`).
- Strict dependency direction: Outer infrastructure layers depend on inner domain/application abstractions; inner domain layers depend on **nothing** external.
- Isolation of untrusted sandbox execution (Go-based trusted bootstrap binary in `bootstrap/`).
- First-class, isolated benchmark suite (`benchmark/`) completely decoupled from production runtime.

---

## 2. Dependency Direction & Import Rules

```text
                    ┌─────────────────────────┐
                    │      src/domain/        │
                    │ (Pure Business Entities)│
                    └────────────▲────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │    src/application/     │
                    │(Use Cases & Interfaces) │
                    └────────────▲────────────┘
                                 │
    ┌────────────────┬───────────┼───────────┬────────────────┐
    │                │           │           │                │
┌───┴─────────┐ ┌────┴─────┐ ┌───┴─────┐ ┌───┴──────────┐ ┌───┴──────────┐
│src/providers│ │src/analys│ │src/intel│ │src/llm       │ │src/persist   │
└─────────────┘ └──────────┘ └─────────┘ └──────────────┘ └──────────────┘
    │                │           │           │                │
    └────────────────┴───────────┼───────────┴────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ src/api/ & src/workers/ │
                    │   (Entrypoints & DTOs)  │
                    └─────────────────────────┘
```

### Strict Import Invariants

1. **`domain` imports NOTHING outside Python standard library and `typing`.**
   - No FastAPI, SQLAlchemy, Pydantic, Celery, boto3, or HTTP client imports.
   - Domain models are pure dataclasses or standard Python objects.
2. **`application` imports `domain` and abstraction interfaces.**
   - Application use cases orchestrate operations using interface contracts (e.g., `RepositorySnapshotStorage`, `SandboxLauncher`).
   - No direct database, AWS SDK, or framework dependencies.
3. **`providers`, `analysis`, `intelligence`, `llm`, `persistence`, `execution`, `git` implement `application`/`domain` interfaces.**
   - All vendor-specific and infrastructure code is encapsulated within its respective module.
4. **`api` and `workers` are thin delivery layers.**
   - They handle HTTP serialization/validation, Celery queue management, and tenant context establishment.
   - They immediately delegate work to application use cases.
5. **`bootstrap` (Go binary) is completely independent.**
   - Shares ZERO code with the Python control plane.
   - Interoperates only via signed JSON schemas and HTTP/S3 endpoints.
6. **`benchmark` imports application interfaces but is NEVER imported by `src/`.**

---

## 3. Top-Level Repository Directory Structure

```text
api-guardian/
├── ARCHITECTURE.md                  # System architecture specification
├── CODE_ARCHITECTURE.md             # Code layout & ownership rules (this file)
├── README.md                        # Developer onboarding & build commands
├── pyproject.toml                   # Python dependencies & tool configs (uv/poetry, ruff, mypy)
├── Makefile                         # Unified development targets (test, lint, build, sandbox)
├── docker-compose.yml               # Local dev infrastructure (Postgres, Redis, LocalStack, Squid)
├── .gitignore
├── .env.example
│
├── src/
│   └── api_guardian/                # Python Core Package (Modular Monolith)
│       ├── __init__.py
│       ├── domain/                  # Pure business concepts & entities
│       ├── application/             # Use cases, orchestrators, interface definitions
│       ├── api/                     # FastAPI HTTP controllers, routes, middleware, DTOs
│       ├── providers/               # Provider capability adapters (Stripe, OpenAI, etc.)
│       ├── analysis/                # Code parsers, Common Code Model, Dependency Graph
│       ├── intelligence/            # Deterministic impact gates & evidence evaluation
│       ├── llm/                     # LLM Gateway, prompt envelopes, token budgeting
│       ├── execution/               # Control-plane sandbox orchestration & capability minting
│       ├── git/                     # Safe subprocess Git execution & archive manager
│       ├── persistence/             # SQLAlchemy ORM, Postgres RLS, Redis, S3 adapters
│       └── workers/                 # Celery task definitions (thin entrypoints)
│
├── bootstrap/                       # Trusted Sandbox Entrypoint (Go Binary Project)
│   ├── go.mod
│   ├── go.sum
│   ├── main.go                      # Entrypoint (PID 1 inside Fargate container)
│   ├── config.go                    # Capability env var parsing & sanitization
│   ├── plan.go                      # VerificationPlan capture & manifest builder
│   ├── audit.go                     # Patch Audit execution (protected files & test scope)
│   └── result.go                    # HMAC-SHA256 result signing & S3 upload
│
├── benchmark/                       # Evaluation & Benchmark Subsystem
│   ├── runner.py                    # Benchmark pipeline execution engine
│   ├── metrics.py                   # Precision/recall & integrity metric calculators
│   └── fixtures/                    # Test fixture repositories & expected impact manifests
│
├── infrastructure/                  # Infrastructure as Code & Environment Configs
│   ├── docker/                      # Dockerfiles for API, Worker, Bootstrap, Squid
│   ├── terraform/                   # AWS Terraform modules (VPC, Fargate, S3, RDS, Proxy)
│   └── squid/                       # Egress proxy whitelist configuration (`squid.conf`)
│
├── tests/                           # Control Plane Test Suite
│   ├── unit/                        # Domain & pure function unit tests
│   ├── integration/                 # Database, S3, provider adapter integration tests
│   ├── security/                    # RLS, credential sanitization, audit verification tests
│   └── e2e/                         # End-to-end pipeline tests (ProviderChange → PR)
│
└── scripts/                         # Operational & Development Tooling
    ├── dev_setup.sh                 # Environment initialization script
    └── run_migrations.sh            # Database migration runner
```

---

## 4. Subsystem & Module Ownership Breakdown

### 4.1 `src/api_guardian/domain/`

Pure, side-effect-free business rules and domain state objects.

| File | Responsibility |
|---|---|
| `organization.py` | `Organization`, `TenantContext` value objects |
| `repository.py` | `Repository`, `RepositoryRevision` (value object), `RepositorySnapshot` entity |
| `provider_change.py` | `ProviderChange`, `CandidateChange`, `VersionGraph`, canonical change IDs |
| `maintenance.py` | `MaintenanceCase` aggregate root, state machine transitions, `ImpactAssessment` |
| `migration.py` | `MigrationCampaign`, `MigrationAttempt`, `PatchArtifact` (with content hashes) |
| `verification.py` | `VerificationPlan`, `VerificationRun`, `VerificationResult` domain objects |
| `pull_request.py` | `PullRequest` aggregate root and lifecycle states |
| `exceptions.py` | Domain-specific exceptions (`DomainError`, `InvalidStateTransitionError`) |

---

### 4.2 `src/api_guardian/application/`

Use case handlers and abstract interfaces (ports).

| Module / File | Responsibility |
|---|---|
| `interfaces/repositories.py` | Storage interfaces (`MaintenanceCaseRepository`, `SnapshotRepository`) |
| `interfaces/sandbox.py` | Execution plane interfaces (`SandboxOrchestrator`) |
| `interfaces/llm.py` | LLM Gateway abstract interface |
| `interfaces/github.py` | GitHub platform integration interface |
| `use_cases/sync_provider.py` | Ingest raw provider artifacts & detect changes |
| `use_cases/analyze_repository.py` | Construct `RepositorySnapshot` & dependency graph |
| `use_cases/assess_impact.py` | Run impact funnel for a `ProviderChange` against snapshot |
| `use_cases/generate_migration.py` | Construct LLM context & produce candidate `PatchArtifact` |
| `use_cases/execute_verification.py` | Prepare `VerificationPlan`, launch sandbox, handle signed result |
| `use_cases/create_pull_request.py` | Validate target HEAD, check non-stale, open GitHub PR |

---

### 4.3 `src/api_guardian/providers/`

Provider capability adapters. Translates raw API documentation/specs into canonical `ProviderChange` objects.

| File | Responsibility |
|---|---|
| `contracts.py` | `ProviderAdapter` base class & capability protocols |
| `registry.py` | Provider adapter registration and lookup factory |
| `stripe/adapter.py` | Stripe OpenAPI diffing & changelog parsing adapter |
| `openai/adapter.py` | OpenAI API versioning & model deprecation adapter |
| `twilio/adapter.py` | Twilio API versioning adapter |
| `github/adapter.py` | GitHub REST/GraphQL API versioning adapter |

---

### 4.4 `src/api_guardian/analysis/`

Language parsing, static analysis, and Common Code Model extraction.

| File | Responsibility |
|---|---|
| `models.py` | Common Code Model (`File`, `Module`, `Symbol`, `CallSite`, `DependencyEdge`) |
| `python/analyzer.py` | AST analyzer for Python (`ast` module based) |
| `javascript/analyzer.py` | AST / Tree-sitter analyzer for JS/TS |
| `graph_builder.py` | Aggregates code models into project-level `DependencyGraph` |

---

### 4.5 `src/api_guardian/intelligence/`

Deterministic evaluation & impact funnel.

| File | Responsibility |
|---|---|
| `deterministic_gates.py` | Fast file, package, and symbol matching logic |
| `evidence_collector.py` | Aggregates proof paths into `ImpactAssessment` evidence chains |

---

### 4.6 `src/api_guardian/llm/`

LLM Gateway, prompt envelopes, and cost/safety wrappers.

| File | Responsibility |
|---|---|
| `gateway.py` | Unified LLM caller with role routing and circuit breakers |
| `prompts.py` | Structured XML-delimited prompt envelopes for migration generation |
| `schema.py` | Pydantic output schemas for LLM structured responses |
| `budget.py` | Token limits and spend tracking per tenant |

---

### 4.7 `src/api_guardian/execution/`

Control-plane orchestration of Fargate execution tasks.

| File | Responsibility |
|---|---|
| `orchestrator.py` | Launches ECS Fargate tasks via `boto3` without Task Role credentials |
| `capability_minting.py` | Generates short-lived presigned GET/PUT URLs and HMAC signing secrets |

---

### 4.8 `src/api_guardian/persistence/`

Database models, storage adapters, and tenant RLS enforcement.

| File | Responsibility |
|---|---|
| `database.py` | SQLAlchemy engine, session management, and `SET LOCAL app.current_tenant_id` context |
| `models/` | SQLAlchemy ORM table definitions matching domain entities |
| `repositories/` | Concrete implementations of application storage interfaces |
| `s3_storage.py` | Storage adapter for S3 (snapshots, patches, verification results) |
| `redis_client.py` | Redis client for Celery broker and locks |

---

### 4.9 `src/api_guardian/api/` & `workers/`

Delivery mechanisms.

| Module | Responsibility |
|---|---|
| `api/app.py` | FastAPI application initialization, CORS, error handlers |
| `api/middleware.py` | Tenant identification middleware, request logging |
| `api/routes/` | REST routers (`webhooks.py`, `cases.py`, `repositories.py`) |
| `workers/celery_app.py` | Celery application configuration & queue setup |
| `workers/tasks/` | Thin worker tasks delegating directly to use cases |

---

## 5. Forbidden Imports & Architectural Constraints

To prevent boundary decay, automated linting rules (via `import-linter` or custom `pytest` rules) enforce:

1. **No Domain Pollution:**
   `src/api_guardian/domain` MUST NOT import `fastapi`, `sqlalchemy`, `celery`, `boto3`, `requests`, `httpx`, or `pydantic`.
2. **No Provider Cross-Contamination:**
   `src/api_guardian/providers/stripe` MUST NOT import from `src/api_guardian/providers/openai`.
3. **No Direct Execution in Control Plane:**
   Control plane code MUST NOT execute untrusted repository build scripts or test runners directly. All execution must go through `src/api_guardian/execution/orchestrator.py`.
4. **No LLM in Deterministic Gates:**
   `src/api_guardian/intelligence/deterministic_gates.py` MUST NOT import `src/api_guardian/llm`.
5. **No Benchmark Runtime Imports:**
   `src/api_guardian/` MUST NOT import from `benchmark/`.

---

## 6. Execution Plane & Trusted Bootstrap Boundary

The execution plane code (`bootstrap/`) is a standalone Go program:

- Built into a scratch/distroless container image: `api-guardian-bootstrap:latest`.
- Configured as container `ENTRYPOINT ["/bootstrap"]`.
- Runs as PID 1 inside the ephemeral Fargate task.
- Consumes capabilities (`SNAPSHOT_URL`, `PATCH_URL`, `RESULT_URL`, `SIGNING_SECRET`), executes baseline and patched runs, performs Patch Audit, signs `VerificationResult`, uploads to S3, and exits.
- Completely isolated from control plane Python source code.

---

## 7. Phased Implementation Roadmap

### Initial Skeleton (Pre-Milestone 1)
- Root build and configuration files (`pyproject.toml`, `Makefile`, `docker-compose.yml`).
- Directory structure with `__init__.py` files.
- Domain entity data classes (`domain/`).
- Abstract storage and service interfaces (`application/interfaces/`).
- Basic FastAPI shell and database session setup with RLS middleware.
- Go bootstrap project skeleton (`bootstrap/`).

### Milestone 1 Additions
- `providers/` (Stripe adapter initial implementation).
- `analysis/` (Python AST parser & Common Code Model).
- `intelligence/` (Deterministic file & symbol gates).
- `persistence/` (Postgres models & S3 snapshot storage).

### Milestone 2+ Additions
- Additional providers (`openai`, `twilio`, `github`).
- JS/TS AST parser in `analysis/javascript/`.
- Full Fargate orchestrator in `execution/`.
- Benchmark runner & fixtures (`benchmark/`).
