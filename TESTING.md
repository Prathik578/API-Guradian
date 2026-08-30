# Testing

API Guardian uses strict testing principles ensuring platform stability.

## Test Suites
1. **Unit Tests**: Foundational tests for core domain logic, algorithms, and isolation layers. (Run via `pytest tests/unit`)
2. **Integration Tests**: End-to-End simulation of user workflows (Signup -> Onboard -> Configure -> Sync) verifying multi-tenant boundaries. (Run via `pytest tests/integration`)
3. **Verification Tests**: Used within Sandbox execution environments to validate LLM-generated code migrations.

## Quality Assurance Metrics
We enforce zero-tolerance for implicit behavior. MyPy is utilized across the Python codebase for strict typing, and ESLint is used across the Next.js frontend to ensure syntactic safety.
