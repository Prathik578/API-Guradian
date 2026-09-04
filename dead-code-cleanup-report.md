# Dead Code Cleanup Report

## Removed
* `tests/runtime/phase25x/test_aws_preflight.py`
  * `cli_available`: Unused local variable setup that was not asserted or used functionally.
  * **Confidence**: HIGH
* `tests/runtime/phase25x/test_s3_iam.py`
  * `s3_client`, `bucket_name`, `tenant_a`, `tenant_b`, `region`: Setup for mocked S3 test that had no assertions utilizing these variables.
  * **Confidence**: HIGH
* `tests/runtime/phase25x/test_s3_runtime.py`
  * `expected_hash`: Hash logic setup for a negative test but never passed as an assertion.
  * **Confidence**: HIGH
* `tests/integration/test_concurrency_proof.py`
  * `tenant_id`, `ctx`, `l1`: Unused setup instances of `uuid` and `TenantContext` not strictly required in mocked/monkey-patched thread simulation logic.
  * **Confidence**: HIGH
* `tests/integration/test_auth_flow.py`
  * `org_b`: Assigned but unread json response of the onboarding sequence for the Tenant B. 
  * **Confidence**: HIGH
* `src/api_guardian/workers/tasks/repository.py`
  * `clone_url`: Local variable holding a github clone URL string that was not actually referenced within the scope.
  * **Confidence**: HIGH
* **Various files**:
  * Unused imports detected and cleaned by `ruff` check.
  * **Confidence**: HIGH

## Retained
* `tests/unit/test_rbac.py`
  * `owner_route`, `admin_route`, `member_route`, `viewer_route`: Detected as unused by `vulture`, but actually routed internally via the FastAPI framework during test execution. 
  * **Why it was preserved**: Frame-work specific execution behavior cannot be statically analyzed via traditional tooling.
* **Database Models and PyDantic Schemas** (`src/api_guardian/persistence/models/tables.py`, etc)
  * Properties flagged as unused dynamically mapped via SQLAlchemy/ORM patterns or HTTP contracts. 
  * **Why it was preserved**: Strong likelihood of serialization/deserialization dependencies mapping to database tables.
* **Feature/Fixture Repositories** (`tests/fixtures/repositories/deprecated_api_python/src/payments.py`)
  * Fake codebase intended for testing the system itself against "dead code", so removing these files would break the intention of the fixture.
  * **Why it was preserved**: Mock source data. 

## Summary
* **Candidates investigated**: 50+
* **Candidates removed**: ~15 unused local variables and missing/unused imports.
* **Candidates retained**: All framework bindings, database models, and fixture sources.
* **Files changed**: 11
* **Approximate lines removed**: ~25 lines. 
* **Validation status**:
  * Tests: PASS 
  * Lint (ruff): PASS (only style warnings remain, no errors)
  * Type check (mypy): PASS 
  * Static analysis: PASS 
  * Build: NOT RUN (No build step in python API aside from pytest dependencies).
* **Remaining concerns**: None. 

All cleanup execution was safely restricted to purely unused local variable scopes without altering structural, runtime, or framework behaviors.
