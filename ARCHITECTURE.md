# API Guardian — Architecture

**Status:** Approved for MVP implementation — all corrections integrated
**Version:** 1.0
**Date:** 2026-08-22

## 1. Purpose

API Guardian is a developer-infrastructure SaaS that detects meaningful changes in third-party APIs, determines whether a customer's code is affected, generates a migration, verifies the migration in an isolated environment, and opens a pull request for human review.

### MVP promise

> Detect a relevant API change, identify affected customer code, produce a verified migration, and open a PR.

### Initial providers

- Stripe
- OpenAI
- Twilio
- GitHub

The architecture must support additional providers without changing the provider-agnostic core.

---

## 2. Architectural Principles

1. **Correctness before autonomy.** Evidence and deterministic checks gate LLM actions.
2. **Untrusted execution.** Customer repositories, dependencies, test scripts, and generated code are untrusted.
3. **Provider independence.** Provider-specific logic terminates at the provider adapter boundary.
4. **Evidence-backed decisions.** Important conclusions must be traceable to stored evidence.
5. **Immutable analysis context.** Analyses and patches are bound to exact repository revisions.
6. **Verification is independent of the LLM.** The model cannot declare its own work successful.
7. **Idempotency is durable.** PostgreSQL is the source of truth for deduplication and durable state; Redis is an optimization, not the authority.
8. **Tenant isolation is defense-in-depth.** Authorization, database isolation, storage isolation, job binding, and execution isolation all apply.
9. **Bounded automation.** Every expensive operation has explicit time, size, concurrency, and cost limits.
10. **MVP restraint.** Prefer a modular monolith plus workers over distributed microservices unless a concrete constraint requires separation.

---

## 3. System Boundary

```text
                         API Guardian
                              |
              +---------------+---------------+
              |                               |
       TRUSTED CONTROL PLANE          UNTRUSTED EXECUTION PLANE
              |                               |
       API / workers / DB                sandboxed task
       provider ingestion               customer code
       orchestration                    build/test scripts
       LLM gateway                      dependencies
       GitHub integration               generated patch
              |                               |
              +----------- controlled -------+
                          handoffs
```

The control plane owns durable state, credentials, orchestration, and policy.

The execution plane runs arbitrary repository code and must not have access to control-plane secrets or internal services.

---

## 4. Deployment Style

### MVP

**Modular monolith + asynchronous workers + ephemeral sandbox execution.**

Do not introduce Kafka, Kubernetes, service meshes, Temporal, or a fleet of independently deployed microservices for MVP.

### Logical modules

- API / HTTP layer
- authentication / authorization
- repository integration
- repository acquisition
- repository intelligence
- dependency graph
- provider intelligence
- change/provenance pipeline
- impact engine
- migration engine
- verification orchestration
- Git/PR integration
- notification
- LLM gateway
- policy / safety layer

These modules may run in the same application deployment initially.

---

## 5. Control Plane

The trusted control plane contains:

- Next.js web application
- FastAPI API
- background workers
- PostgreSQL
- Redis queue/cache
- provider ingestion
- GitHub integration
- LLM gateway
- orchestration/policy logic

### Control-plane responsibilities

- authenticate and authorize users
- manage organizations and repositories
- receive and validate GitHub webhooks
- ingest provider changes
- store domain state
- build analysis jobs
- orchestrate migrations
- launch sandbox executions
- evaluate verification results
- create PRs
- record audit/provenance information

Customer repository code must **never** execute inside the main API process.

---

## 6. Execution Plane

Execution is performed in ephemeral isolated tasks.

Conceptually:

```text
Trusted bootstrap
      |
      v
Exact repository snapshot
      |
      v
Ephemeral execution environment
      |
      +--> baseline verification
      +--> capture VerificationPlan
      +--> fresh workspace from same snapshot
      +--> apply patch
      +--> patch audit
      +--> run same VerificationPlan
      |
      v
Trusted result collection
      |
      v
Task destroyed
```

### Execution-plane rules

The customer-code process receives:

- no database credentials
- no control-plane credentials
- no LLM API keys
- no AWS credentials of any kind (no task IAM role is assigned)
- no GitHub installation token
- no pre-signed S3 URLs
- no result-signing secrets

The Fargate task is configured with:

- **Task execution role**: Used by ECS infrastructure to pull container images and write CloudWatch logs. Not accessible to application or customer code.
- **Task role**: Not assigned (`null`). No IAM role exists for the task. The ECS credential metadata endpoint returns no credentials.

Any bootstrap capability used to acquire an input artifact must be consumed and deleted from the process environment before untrusted repository code begins executing.

The exact bootstrap implementation must preserve this invariant on the selected execution platform.

---

## 7. Domain Model

### ProviderChange

Canonical immutable interpretation of a provider change.

Contains, where available:

- provider
- provider-native identifier
- canonical identifier
- source artifacts
- change classification
- affected API entities
- API/version context
- effective/sunset dates
- evidence references

### Repository

Customer-managed codebase registered with API Guardian.

### RepositoryRevision (value object)

Represents a logical point in repository history:

- repository ID
- branch/ref
- commit SHA

This is the logical identity. It does not guarantee physical content equivalence — the same commit SHA cloned at different times could theoretically differ if Git history is rewritten. Use `RepositorySnapshot` for physical verification.

### RepositorySnapshot

Immutable analysis context representing the physical, verifiable archive of a repository at a specific revision:

- `RepositoryRevision` (repository + branch + commit SHA)
- archive content hash (SHA-256 of the snapshot archive)
- analysis timestamp
- dependency graph
- code-model version

The architecture proves that the exact repository state analyzed is the exact state verified by comparing both the commit SHA and the archive content hash.

### VerificationPlan (immutable artifact)

Generated from the base repository revision before any migration is applied:

- test command(s)
- working directory
- test roots / test file inventory (paths and hashes)
- test framework identifier
- build command (if applicable)
- typecheck command (if applicable)
- lint command (if applicable)
- baseline test count
- baseline skip count
- configuration file hashes (for protected files)

The migration patch cannot redefine the VerificationPlan. The same plan is executed for both baseline and patched verification. If the patch alters any protected configuration, the Patch Audit detects it by comparing file hashes against the plan.

### MaintenanceCase

Aggregate root representing:

> A specific external change affecting a specific customer repository at a specific revision/branch context.

Owns the lifecycle connecting impact, migration, verification, and PR state.

### ImpactAssessment

Evidence-backed determination of whether the repository snapshot is affected.

### MigrationCampaign

Workflow for resolving an affected MaintenanceCase.

### MigrationAttempt

One generation/repair attempt by the migration system.

### VerificationRun

Structured result of running baseline and patched verification, bound to a specific `VerificationPlan`.

### PatchArtifact

Immutable patch bound to:

- repository
- base commit SHA
- archive content hash (the physical snapshot it was generated against)
- affected files
- pre-image hashes
- patch data
- post-image hashes

### PullRequest

GitHub PR created from a verified patch.

---

## 8. Core Domain Relationship

```text
ProviderChange
      |
      +-----------------------+
                              |
Repository --> RepositorySnapshot
                              |
                              v
                       MaintenanceCase
                              |
                              v
                      ImpactAssessment
                              |
                              v
                      MigrationCampaign
                              |
                     +--------+--------+
                     |                 |
                     v                 v
             MigrationAttempt     VerificationRun
                                       |
                                       v
                                Verified PatchArtifact
                                       |
                                       v
                                   PullRequest
```

---

## 9. Temporal Model

Every analysis and migration is tied to an exact repository revision.

Required context:

- repository ID
- branch/ref
- commit SHA
- dependency graph revision
- provider/API version context
- provider change revision
- analysis timestamp

### Reproducibility invariant

A migration must be reproducible from:

```text
ProviderChange
+ RepositorySnapshot
+ Evidence
+ Migration context
+ model/policy configuration
+ PatchArtifact
```

### Stale rule

Before creating a PR, the system must read the current target-branch HEAD.

If it no longer matches the revision used for verified migration, the system must **not** create the PR without revalidation/reverification.

Repository changes may invalidate active campaigns.

---

## 10. Provider Architecture

Providers are capability-oriented adapters.

### Conceptual capabilities

- `SourceAcquisition`
- `ChangeDetection`
- `ChangeInterpretation`
- `SchemaRetrieval` (optional)
- `VersionGraphResolution` (optional)
- provider-specific validation where required

The provider layer produces provider-agnostic domain representations.

### Provider boundary

```text
Stripe
OpenAI
Twilio
GitHub
   |
   v
Provider Adapter Layer
   |
   v
RawArtifact / CandidateChange / ProviderChange
   |
   v
Core Maintenance Engine
```

The core engine must not contain provider-specific branching such as `if stripe ... else github ...` except where a provider capability is explicitly modeled.

---

## 11. Provider Source Pipeline

Provider ingestion is separated into distinct stages:

```text
Source
  |
  v
RawArtifact + hash
  |
  v
ChangeDetection
  |
  v
CandidateChange
  |
  v
ChangeInterpretation
  |
  v
Canonical ProviderChange
```

### RawArtifact

Immutable representation of provider source used for interpretation.

May include:

- HTML
- JSON
- OpenAPI
- RSS/Atom
- release metadata
- official migration documentation

### Source precedence

When sources conflict, deterministic/authoritative provider artifacts take precedence over LLM interpretation.

The LLM may interpret evidence; it does not silently override authoritative schema/version facts.

---

## 12. Change Identity and Versioning

Provider changes must have stable identities.

Preferred identity sources:

1. provider-native identifier
2. canonical source identifier
3. deterministic semantic composite/hash fallback

Edited source material creates a new revision of the source/change representation rather than silently rewriting history.

API version evolution is modeled as a **version graph**, not a universal semantic-version linked list.

The graph must support:

- semantic versions
- date-based versions
- API versions
- SDK versions
- compatibility relationships
- deprecations
- non-linear evolution

---

## 13. Repository Acquisition

Repository acquisition is a controlled subsystem and is not performed as arbitrary code execution inside the FastAPI process.

Requirements:

- shallow clone where possible
- disable Git hooks
- `GIT_TERMINAL_PROMPT=0`
- no submodules by default
- no Git LFS by default unless explicitly supported
- repository size limits
- file count limits
- archive size limits
- safe path handling
- symlink policy
- exact commit verification

The acquisition layer must produce an immutable repository snapshot for downstream analysis/execution.

---

## 14. Repository Intelligence

The architecture uses language-specific analysis to produce a **language-neutral Common Code Model**.

Conceptual model:

```text
File
  -> Module
      -> Symbol
          -> CallSite
              -> API Entity

DependencyEdge
```

The core impact engine operates on this common model, not on parser-specific AST structures.

### MVP language policy

Full analysis support is initially prioritized for:

- Python
- JavaScript / TypeScript

Other languages may be:

- heuristic-only
- partial
- unsupported

The architecture must allow additional language adapters later.

---

## 15. Dependency Graph

The dependency graph represents relationships such as:

```text
Repository
  -> Project / Service
      -> Provider
          -> API Entity
              -> endpoint / SDK method / webhook
                  -> CodeReference
```

Monorepositories must be able to represent multiple projects/services and multiple dependency graphs within one repository snapshot.

`Project` may remain derived analysis metadata unless later product requirements justify promoting it to a first-class entity.

---

## 16. Impact Engine

Impact analysis uses a cost-bounded funnel.

```text
ProviderChange
      |
      v
Repository/provider gate
      |
      v
File/candidate gate
      |
      v
Symbol/API-entity gate
      |
      v
Semantic analysis only when necessary
      |
      v
ImpactAssessment
```

### Evidence strength

Use categorical evidence levels such as:

- direct symbol/API match
- alias/wrapper match
- dynamic dispatch
- semantic inference

Do not expose fake mathematical precision.

Separate "Evidence strength" from "Impact classification".

Possible classifications:

- `Confirmed_Affected`
- `Likely_Affected`
- `Not_Affected`
- `Human_Review_Required`

---

## 17. Provenance

Every important decision must be explainable through an evidence chain.

```text
Provider source
   -> RawArtifact
   -> CandidateChange
   -> ProviderChange
   -> Dependency evidence
   -> Code reference
   -> ImpactAssessment
   -> MigrationAttempt
   -> VerificationRun
   -> PullRequest
```

Evidence may include:

- source URL
- source artifact hash
- schema diff
- file path
- symbol
- source range
- dependency edge
- analysis output
- migration guidance
- verification output

---

## 18. Migration Engine

The migration engine receives curated context rather than full repositories by default.

Context may include:

- ProviderChange
- migration guidance
- relevant code symbols/files
- dependency graph evidence
- repository conventions
- relevant tests
- repository revision

The migration model produces an immutable PatchArtifact.

### Patch requirements

Every patch is bound to:

- base commit SHA
- file path
- pre-image hash
- patch hunks
- post-image hash

Patch application must fail deterministically if the expected file state no longer matches.

---

## 19. Patch Scope Policy

Generated patches are checked by a trusted policy layer before verification.

The policy detects:

- files outside declared scope
- unexpected directories
- test modifications
- CI configuration changes
- dependency changes
- lockfile changes
- secret/configuration changes
- executable permission changes
- symlink creation
- suspicious path changes

Changes outside the declared migration scope are rejected or escalated for human review.

MVP does not permit a migration to silently weaken its own verification environment.

---

## 20. Verification Engine

Verification is a first-class domain process.

```text
RepositorySnapshot @ commit A
        |
        v
Create baseline workspace
        |
        v
Run baseline verification
        |
        v
Capture immutable VerificationPlan + baseline test manifest
        |
        v
Create FRESH workspace from EXACT same snapshot
        |
        v
Apply PatchArtifact
        |
        v
Patch Audit (compare patch against VerificationPlan)
        |
        v
Run the SAME immutable VerificationPlan
        |
        v
Compare baseline vs patched results
        |
        v
Produce VerificationRun
```

**Critical ordering invariant:** The VerificationPlan is captured from the baseline workspace before any patch is applied. The patched workspace is created from a fresh extraction of the same snapshot archive. The migration never has the opportunity to alter the verification procedure.

### Verification stages

1. Baseline workspace creation (extract snapshot)
2. Baseline dependency installation
3. Baseline test/build/lint execution
4. VerificationPlan capture (test inventory, config hashes, commands)
5. Fresh patched workspace creation (re-extract same snapshot)
6. Patch integrity verification (pre-image hash check)
7. Patch application
8. Patch Audit (scope check, config integrity, test inventory comparison)
9. Patched dependency installation
10. Patched test/build/lint execution using the immutable VerificationPlan
11. Result comparison (baseline vs patched)
12. Structured VerificationRun production

### Result classes

At minimum distinguish:

- `Verified` — baseline passed, patch applied, audit passed, patched tests passed
- `Baseline_Failed` — base repository tests fail without any patch
- `Patch_Conflict` — pre-image hash mismatch, patch cannot apply
- `Audit_Failed` — patch modifies protected files/tests outside declared scope
- `Tests_Failed` — patched tests fail where baseline passed
- `Infrastructure_Failed` — sandbox/dependency/environment error
- `Timeout` — execution exceeded deadline
- `No_Test_Command` — no discoverable test command
- `Expired` — task exceeded reaper deadline without reporting

Verification is not defined as simply "exit code 0".

---

## 21. Verification Integrity

The migration cannot freely modify the mechanism used to evaluate itself.

### VerificationPlan immutability

The test commands, test file inventory, and configuration file hashes are captured during baseline execution. The patched workspace is evaluated using the exact same VerificationPlan. If the patch has altered any protected configuration, the Patch Audit detects it by comparing file hashes.

### Protected files (MVP defaults — forbidden to modify without explicit scope)

- `pytest.ini`, `pyproject.toml` (pytest/tool config sections), `setup.cfg` (tool sections)
- `jest.config.*`, `vitest.config.*`
- `package.json` `scripts.test` field
- `Makefile` test targets
- `.eslintrc*`, `tsconfig.json`
- CI configuration (`.github/workflows/*`, `.gitlab-ci.yml`)
- Test runner configuration

### Allowed with explicit migration scope

A migration may remove or modify tests only when the migration scope explicitly declares it. Example: if the provider change removes an endpoint entirely and the customer has tests specifically for that endpoint, the migration scope may declare the specific test files as removable. The Patch Audit permits those declared files but rejects any other test modifications.

### Verification coverage rule

> Verification coverage must not be weakened without explicit migration scope authorization.

This means:

- Test deletion without scope declaration → `Audit_Failed`
- New test skips without scope declaration → `Audit_Failed`
- Modification of protected configuration → `Audit_Failed`
- Reduction of executed test scope → `Audit_Failed`

A legitimate migration may occasionally remove obsolete tests, so "more tests is always correct" is not encoded as a universal law. Instead, test removal requires explicit scope declaration.

The migration model cannot declare verification success.

Only the trusted verification subsystem can create a `Verified` result.

---

## 22. Sandbox Security

Customer code is hostile by default.

The execution environment must provide:

- no inbound access
- no control-plane network access
- no database access
- no internal service access
- no credentials of any kind (no task IAM role assigned)
- bounded CPU
- bounded memory
- bounded runtime
- bounded storage
- controlled outbound networking through explicit egress proxy

### Network topology

```text
VPC-B (Execution)
├── Sandbox Subnet (private, no IGW, no NAT)
│   ├── Fargate tasks
│   └── Route table: only route → Proxy Subnet via VPC routing
│
├── Proxy Subnet (private, with NAT Gateway for egress)
│   └── Squid egress proxy
│       ├── Domain allowlist (npm, pypi, maven, nuget, rubygems, golang)
│       ├── Rate limit: 100 connections/min per source IP
│       ├── Bandwidth limit: 500MB total egress per task
│       └── All requests logged with task ID
│
└── Route 53 Resolver DNS Firewall
    ├── Allowlist: approved registry domains
    └── Default action: BLOCK (return NXDOMAIN)
```

### Security group rules

**Sandbox ENI:**

- Ingress: none
- Egress: TCP 3128 to proxy security group only. All other egress denied.

**Proxy ENI:**

- Ingress: TCP 3128 from sandbox security group only
- Egress: TCP 443 to `0.0.0.0/0` (via NAT Gateway, filtered at proxy application layer)

### DNS enforcement

Route 53 Resolver DNS Firewall is a supported AWS service that filters DNS queries at the VPC resolver level. Sandbox tasks use the VPC DNS resolver (default). The firewall allowlists only approved package registry domains. All other queries receive `NXDOMAIN`. This prevents DNS tunneling because arbitrary external domains cannot be resolved.

### Raw IP bypass prevention

The sandbox subnet has no route to a NAT Gateway or Internet Gateway. Its only route is to the proxy subnet. Even if code constructs a raw IP connection (bypassing DNS), the security group only permits TCP 3128 to the proxy. Direct IP connections to arbitrary addresses are dropped at the ENI level.

### Residual risk

A process that resolves an allowlisted domain and then sends crafted HTTP requests to that domain could encode small amounts of data in URL paths, headers, or request bodies. Rate limits and bandwidth caps make bulk exfiltration impractical. All proxy requests are logged for forensic analysis.

---

## 23. Sandbox Bootstrap

Bootstrap capabilities are considered secrets/capabilities even when implemented as presigned URLs.

### Bootstrap environment

```text
Container image (immutable, built by API Guardian):
├── /bootstrap              (root-owned, read-only, compiled binary)
├── /workspace              (tmpfs, writable, customer code goes here)
└── root filesystem         (read-only via Fargate readonlyRootFilesystem)
```

### Bootstrap capability lifecycle

The Fargate task receives these environment variables at launch:

| Variable | Purpose | Lifetime |
| --- | --- | --- |
| `SNAPSHOT_URL` | Pre-signed S3 GET URL for repository archive | 10 minutes |
| `PATCH_URL` | Pre-signed S3 GET URL for PatchArtifact | 10 minutes |
| `RESULT_URL` | Pre-signed S3 PUT URL for result upload | 30 minutes |
| `EXPECTED_SNAPSHOT_HASH` | SHA-256 of expected archive | Consumed during bootstrap |
| `EXPECTED_PATCH_HASH` | SHA-256 of expected patch | Consumed during bootstrap |
| `ATTEMPT_ID` | Unique verification attempt identifier | Included in result |
| `NONCE` | Replay-prevention token | Included in result |
| `SIGNING_SECRET` | HMAC-SHA256 key for result authentication | Used only by bootstrap |

URL lifetimes are set with a safety margin: snapshot/patch GET URLs (10 min) expire well before the task hard timeout (20 min). The result PUT URL (30 min) remains valid beyond the task timeout to allow result upload even in slow-completion scenarios.

### Bootstrap sequence (trusted binary, PID 1)

```text
 1.  Download snapshot from SNAPSHOT_URL
 2.  Verify SHA-256 == EXPECTED_SNAPSHOT_HASH
 3.  Download patch from PATCH_URL
 4.  Verify SHA-256 == EXPECTED_PATCH_HASH
 5.  DELETE all env vars (URLs, secrets) from own process environment
 6.  Extract snapshot to /workspace/baseline
 7.  ── BASELINE PHASE ──
 8.  Run dependency install in /workspace/baseline
 9.  Discover and run test command in /workspace/baseline
10.  Capture VerificationPlan:
       - test command
       - test file inventory (paths + hashes)
       - config file hashes (protected files)
       - test count, skip count
11.  ── PATCHED PHASE ──
12.  Extract snapshot AGAIN to /workspace/patched (fresh copy)
13.  Apply PatchArtifact to /workspace/patched
14.  Verify pre-image hashes match
15.  ── PATCH AUDIT ──
16.  Compare patched config file hashes against VerificationPlan
17.  Compare patched test inventory against VerificationPlan
18.  Check patch scope (no files outside declared scope)
19.  If audit fails → record Audit_Failed result, skip to step 23
20.  ── PATCHED VERIFICATION ──
21.  Run dependency install in /workspace/patched
22.  Run SAME test command from VerificationPlan in /workspace/patched
23.  ── RESULT COLLECTION ──
24.  Construct VerificationResult JSON (see §24)
25.  HMAC-SHA256 sign the result JSON with SIGNING_SECRET
26.  Upload signed result + truncated logs to RESULT_URL
27.  Exit
```

**Environment sanitization (step 5):** After downloading both artifacts, the bootstrap binary unsets `SNAPSHOT_URL`, `PATCH_URL`, `RESULT_URL`, and `SIGNING_SECRET` from its own process environment. Customer code subprocesses (launched at steps 9 and 22) are `fork/exec`'d with a clean environment containing only `PATH`, `HOME`, `LANG`, `TERM`. Customer code runs as uid 1000 (unprivileged) with no Linux capabilities. Customer code has a 10-minute timeout enforced by bootstrap via `SIGKILL`. Customer code stdout/stderr captured by bootstrap, capped at 10MB.

**Bootstrap crash behavior:** If bootstrap itself crashes or times out (20-minute hard kill by Fargate), the control plane's reaper detects the missing result after the deadline and transitions the VerificationRun to `Infrastructure_Failed`.

Untrusted customer processes must not receive reusable access to S3, AWS, GitHub, or control-plane services.

---

## 24. Verification Result Authenticity

Verification results are authenticated to prevent fabrication by customer code.

### Signing model

Three distinct concepts:

- **`attempt_id`**: Identity — which verification attempt this result belongs to
- **`nonce`**: Replay prevention — a random value generated by the control plane per attempt
- **`signing_secret`**: Authentication — an HMAC-SHA256 key generated by the control plane, passed to bootstrap, never written to workspace, deleted from env before customer code

### Result structure

The VerificationResult JSON must bind:

- attempt_id
- nonce
- snapshot content hash
- patch content hash
- baseline exit code, test count, skip count
- patched exit code, test count, skip count
- audit passed/failed with reasons
- overall result classification
- stdout/stderr content hashes
- timestamp

### Control-plane verification

```text
1. Download result JSON from S3
2. Verify HMAC-SHA256 signature using the signing_secret generated at launch
3. Verify attempt_id matches the launched attempt
4. Verify nonce matches
5. Verify snapshot_hash and patch_hash match expected values
6. Parse structured result
7. Reject if attempt already in terminal state (prevent replay)
8. Transition VerificationRun state machine
```

The control plane can distinguish a trusted verification result from an arbitrary file produced by customer code.

Raw sandbox output is diagnostic evidence, not itself the authoritative verification decision.

---

## 25. Data Architecture

### PostgreSQL

Stores durable domain state and metadata:

- organizations
- users
- repositories
- provider metadata
- ProviderChanges
- MaintenanceCases
- RepositorySnapshots metadata
- dependencies
- ImpactAssessments
- MigrationCampaigns
- MigrationAttempts
- VerificationRuns metadata
- PullRequests
- audit events
- durable idempotency records

### Object storage

Stores large artifacts where needed:

- raw provider artifacts
- repository snapshots during controlled handoff
- patches
- verification logs
- model artifacts/prompts where policy permits

### Redis

Used for:

- background queueing
- short-lived locks/caches
- performance optimizations

Redis is **not** the source of truth for correctness-critical deduplication.

---

## 26. Data Retention

Avoid the phrase “zero retention” unless literally true.

### Class A — Metadata

Stored in PostgreSQL according to account retention/deletion policy.

### Class B — Evidence

Code-derived evidence is stored only where necessary and is subject to customer retention/deletion policy.

### Class C — Full source

Prefer ephemeral storage.

If a repository snapshot must enter object storage for controlled handoff, it must have a short, explicit TTL and automatic hard deletion.

### Class D — Diagnostic artifacts

Logs, patches, prompts, and outputs have explicit retention periods and may contain source-derived information.

Customer deletion must cover every persistent store and supported backup/lifecycle path.

---

## 27. Tenant Isolation

Tenant identity must propagate through:

```text
request
 -> authorization context
 -> domain operation
 -> job
 -> worker
 -> artifact
 -> sandbox
 -> verification
 -> notification
```

### Defense in depth

- application authorization
- PostgreSQL RLS (transaction-scoped)
- tenant-bound storage paths/policies
- job-to-tenant binding
- tenant-scoped caches
- tenant-aware logging
- isolated execution

### Transaction-scoped tenant context

Tenant context is transaction-scoped, not connection-lifetime. Every database transaction sets tenant context at the start using `SET LOCAL app.current_tenant_id = ?`. `SET LOCAL` is automatically cleared at transaction end (commit or rollback), so returning the connection to the pool cannot leak tenant context.

- Pooled connections cannot retain the previous tenant's context.
- Background workers load the job record, extract `tenant_id`, and set `SET LOCAL` before any domain queries.
- Admin/migration operations use a separate connection context with RLS explicitly bypassed and audit-logged.
- No normal application query may execute without tenant context being set.

Shared caches must never return tenant-specific source or analysis data across organizations.

---

## 28. Job Architecture

Use asynchronous workers for long-running work.

Initial logical jobs:

- provider ingestion
- repository acquisition
- repository analysis
- impact analysis
- migration generation
- verification orchestration
- PR creation
- notification
- stale detection

### Idempotency

Correctness-critical deduplication is backed by durable database constraints/records.

Redis may reduce duplicate work but cannot be the only guarantee.

### Job identity

Every important job has:

- unique job ID
- tenant binding
- repository binding where applicable
- input artifact/revision binding
- status
- attempt count
- timestamps
- timeout/deadline

---

## 29. Concurrency and Stale State

Before an external side effect such as PR creation:

1. reload current target branch state
2. verify expected revision
3. verify MaintenanceCase is still actionable
4. verify PatchArtifact remains valid
5. verify no competing campaign owns the same work
6. perform the side effect

Repeated webhooks must not create duplicate work.

Repository mutation during migration must invalidate or force revalidation of stale artifacts.

### Manual resolution detection

When a repository advances (push webhook), the system creates a new `RepositorySnapshot` for affected `MaintenanceCases` still in active states. It re-runs the deterministic impact gates against the new snapshot.

If the dependency or API usage that triggered the case no longer exists in the new snapshot (e.g., the customer removed the deprecated API call themselves), the `MaintenanceCase` transitions to `Manually_Resolved`.

This is a semantic check (re-running impact analysis), not a filename-based heuristic.

---

## 30. MaintenanceCase State Machine

Primary states:

```text
Discovered
  -> Impact_Analyzing
  -> Unaffected
  -> Affected_Action_Required
  -> Migrating
  -> Verifying
  -> PR_Open
  -> Resolved
```

Exception/terminal states include:

- Suppressed
- Cancelled
- Stale
- Baseline_Failed
- Unsupported
- Human_Intervention_Required
- Manually_Resolved
- Provider_Change_Reclassified

A case must never remain permanently in an active state without timeout/recovery logic.

Customer may manually suppress or resolve a case.

`Manually_Resolved` is entered when a re-analysis of the repository at a newer commit determines the triggering dependency or API usage no longer exists.

---

## 31. MigrationCampaign State Machine

```text
Pending
  -> Generating
  -> Verifying
  -> PR_Created
```

Failure/recovery paths:

- Blocked
- Generation_Failed
- Verification_Failed
- Infrastructure_Failed
- Stale
- Cancelled
- Human_Intervention_Required

Retries are bounded.

---

## 32. VerificationRun State Machine

```text
Queued
  -> Running
  -> Verified
```

Failure/terminal states:

- Baseline_Failed
- Patch_Conflict
- Tests_Failed
- Verification_Integrity_Failed
- Infrastructure_Failed
- Timeout
- Expired
- Cancelled

A watchdog/reaper must recover jobs that remain in `Running` beyond their lease/deadline.

---

## 33. Pull Request Lifecycle

PR operations are bound to:

- repository
- MaintenanceCase
- PatchArtifact
- verified commit

Possible states:

- Planned
- Creating
- Open
- Merged
- Closed
- Stale
- Creation_Failed

If an open PR becomes stale because the target branch changes, the system must detect and surface that state.

---

## 34. LLM Architecture

Use a model abstraction layer with logical roles:

- `semantic_analysis_model`
- `migration_reasoning_model`
- `patch_review_model`
- `failure_diagnosis_model`

The architecture does not depend on a specific vendor or model name.

### LLM trust boundary

LLMs may:

- interpret evidence
- classify ambiguous cases
- propose transformations
- diagnose failed migrations

LLMs may not authoritatively determine:

- whether a provider change exists
- whether a specific commit was analyzed
- whether a patch applied successfully
- whether tests passed
- whether verification succeeded
- whether a PR is allowed to be created

All repository/provider text entering an LLM is untrusted content and must be clearly delimited from higher-priority instructions.

---

## 35. Cost Controls

Every expensive operation is bounded.

### Repository limits

- maximum repository size
- maximum file count
- maximum scan duration

### Migration limits

- maximum context files
- maximum context bytes
- maximum patch size
- maximum changed lines
- maximum model tokens
- maximum migration attempts
- maximum sandbox runtime

### Tenant limits

- repository count
- concurrent analyses
- concurrent sandboxes
- LLM token budget
- rate limits
- storage limits

### Global limits

- total sandbox concurrency
- queue depth
- LLM spend
- egress capacity

The scheduler/infrastructure must enforce limits, not merely the UI.

---

## 36. LLM Failure Protection

LLM provider failures must not cause unbounded retries.

Use:

- bounded retries
- exponential backoff
- circuit breaker behavior
- global provider health state
- tenant-aware retry limits
- human escalation

A provider-wide outage should quiesce LLM jobs rather than generate large retry storms.

---

## 37. GitHub Integration

Use a GitHub App.

Responsibilities:

- repository authorization
- installation lifecycle
- webhook reception/validation
- repository metadata
- source acquisition
- branch creation
- commit creation
- PR creation
- PR status tracking

Webhook delivery IDs are durably deduplicated.

PR creation is allowed only after all final consistency/safety checks pass.

---

## 38. Benchmark / Evaluation System

A first-class benchmark suite exists alongside production tests.

Fixture repositories cover:

- Stripe
- OpenAI
- Twilio
- GitHub

Benchmarks evaluate:

- dependency detection
- impact precision/recall
- semantic migration correctness
- verification correctness
- verification integrity (attack suite)
- regression behavior

Multiple valid patches are allowed.

Benchmark correctness is based on semantic acceptance criteria, not exact textual equality of generated code.

Verification integrity target: 100% detection across the maintained verification-integrity attack suite. This is not a claim of mathematical completeness against all possible bypasses — it means every known attack pattern in the suite must be detected.

The benchmark suite runs in CI and must be independent of real customer repositories.

---

## 39. Observability

### Operational

- API latency
- 5xx rate
- queue depth
- worker failures
- sandbox boot/runtime
- provider ingestion failures
- GitHub API rate usage

### Correctness

- provider change detection precision/recall
- impact precision/recall
- false-positive rate
- baseline failure rate
- verification pass rate

### Customer value

- time-to-verified-PR
- time-to-accepted-PR
- PR acceptance rate
- human correction rate
- resolved maintenance cases

### Cost

- LLM tokens/cost
- sandbox CPU/runtime
- storage
- network egress
- cost per maintenance case

---

## 40. Security Requirements

The system must enforce:

- least privilege
- tenant isolation
- source-code protection
- secure secret storage
- authenticated webhooks
- sandbox isolation
- controlled egress
- resource limits
- audit logging
- artifact integrity
- data deletion
- prompt-injection containment

No production deployment occurs automatically in MVP.

---

## 41. MVP Boundaries

Do not build in MVP:

- autonomous production deployment
- generic CI replacement
- general security scanning
- full API gateway
- mobile application
- general-purpose code editor
- Kubernetes platform
- Kafka/event-bus platform
- multi-region active-active deployment
- universal language support
- universal API specification framework

Build the smallest system that reliably performs:

```text
API Change
   ↓
Impact
   ↓
Migration
   ↓
Verification
   ↓
PR
```

---

## 42. Build Order

### Phase 1 — Foundation

- repository structure
- authentication
- organizations/tenants
- database schema
- GitHub App integration
- durable job model
- basic observability

### Phase 2 — Repository Intelligence

- repository acquisition
- Python analysis
- JS/TS analysis
- common code model
- dependency graph
- dependency inventory UI

### Phase 3 — Provider Intelligence

- Stripe
- OpenAI
- Twilio
- GitHub
- raw source artifacts
- change normalization

### Phase 4 — Impact Engine

- deterministic gates
- evidence model
- MaintenanceCase
- semantic analysis
- confidence/classification

### Phase 5 — Migration Engine

- curated context builder
- migration model gateway
- PatchArtifact
- patch policy

### Phase 6 — Verification

- isolated execution
- baseline verification
- patch verification
- verification integrity
- structured results

### Phase 7 — PR Automation

- stale checks
- branch creation
- commit
- PR generation
- provenance in PR body

### Phase 8 — Reliability

- benchmark suite
- cost controls
- circuit breakers
- dead-letter/failed-job recovery
- security hardening

---

## 43. Known Deferred Decisions

The following are intentionally deferred until real workload evidence exists:

- extraction of analysis workers into separate services
- more advanced workflow orchestration
- advanced registry/proxy caching
- enterprise customer-hosted execution
- additional language frontends
- additional provider capabilities
- global/multi-region deployment
- advanced real-time dashboard updates

Deferred does not mean ignored; it means the MVP will not pay the complexity cost until evidence requires it.

---

## 44. Non-Negotiable Invariants

The implementation is considered architecturally incorrect if any of these are violated:

1. Customer code never executes in the trusted API process.
2. Customer code cannot access another tenant's data.
3. Customer code has no AWS credentials (no task IAM role is assigned).
4. Customer code has no control-plane credentials, GitHub tokens, LLM keys, or S3 URLs.
5. Bootstrap capabilities are consumed and deleted before customer code starts.
6. A verified patch is tied to an exact repository revision AND a physical snapshot content hash.
7. A stale verified patch cannot silently become a PR (final HEAD check before creation).
8. The migration agent cannot alter the VerificationPlan. The plan is captured from the unmodified baseline.
9. The migration agent cannot declare its own verification success. Only the trusted bootstrap produces signed results.
10. Repeated webhook/job delivery cannot create duplicate logical work (Postgres-backed idempotency).
11. Provider-specific logic cannot leak into the provider-agnostic maintenance engine.
12. Expensive LLM/sandbox execution is bounded by hard resource limits.
13. Tenant context in Postgres is transaction-scoped (`SET LOCAL`), preventing cross-tenant leaks via connection pools.
14. Every PR generated by API Guardian can be traced back to a provider change, affected code, migration artifact, and verification result.

---

## 45. Definition of Done for the Architecture

The architecture is considered implemented correctly when the system can demonstrate this complete flow on benchmark repositories:

```text
Provider source
      ↓
ProviderChange
      ↓
RepositorySnapshot
      ↓
DependencyGraph
      ↓
MaintenanceCase
      ↓
ImpactAssessment
      ↓
MigrationCampaign
      ↓
PatchArtifact
      ↓
Baseline + patched VerificationRun
      ↓
Verified Patch
      ↓
GitHub Pull Request
```

Every stage must be observable, auditable, tenant-bound, and reproducible.

---

## 46. Final Architectural Position

API Guardian MVP is a **modular monolith with asynchronous workers and a strongly isolated execution plane**.

The control plane owns the product state and orchestration.

The execution plane is treated as hostile.

Provider adapters translate heterogeneous external API ecosystems into a normalized provider-change model.

Repository analysis creates a language-neutral dependency representation.

Impact analysis uses deterministic filtering before semantic reasoning.

Migration is constrained by immutable repository revisions and patch scope.

Verification is performed independently of the LLM in an isolated environment and produces a structured, authenticated result.

Only verified, non-stale migrations may become PRs.

This architecture is intentionally sufficient for the MVP without prematurely becoming a distributed platform.
