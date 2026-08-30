# Troubleshooting and Support

API Guardian is a highly complex, distributed system interacting with volatile third-party APIs and massive customer codebases. While we strive for absolute autonomy and perfection, edge cases exist. This guide covers common issues and how to resolve them.

## Common Issues

### 1. Verification Sandbox Fails (Timeout or Out of Memory)
**Symptom:** A Maintenance Case successfully generates a patch, but the Verification stage fails with a `TIMEOUT` or `OOM_KILLED` status.
**Cause:** Your test suite requires more resources than the default Fargate sandbox allocation, or an infinite loop was introduced.
**Resolution:** Navigate to the Repository settings and increase the Sandbox Resource Allocation (Memory/CPU). Ensure your test command only runs necessary unit/integration tests, avoiding long-running UI automation tests if possible.

### 2. AST Parser Misses an API Call
**Symptom:** A Provider Notice is issued, but API Guardian reports a Blast Radius of 0, even though you know the API is used in a repository.
**Cause:** The API call is highly obfuscated, constructed dynamically at runtime via string concatenation, or wrapped in a custom, highly abstracted internal library that the parser cannot resolve.
**Resolution:** You can manually trigger a Maintenance Case for a specific repository from the Provider Notice dashboard. Provide a "Hint" in the trigger dialogue pointing the LLM to the specific wrapper class or utility function.

### 3. Missing `guardian.yml` Configuration
**Symptom:** Pull Requests are being opened without the correct labels or reviewers assigned.
**Cause:** The `guardian.yml` file is missing, incorrectly formatted, or placed in a subdirectory instead of the repository root.
**Resolution:** Validate your `guardian.yml` against our JSON schema in the dashboard. Ensure it is committed directly to the root of the default branch.

## Getting Help
If you encounter an issue that cannot be resolved via configuration, our support infrastructure is ready to assist.
- **Enterprise Support:** Organizations on the Enterprise tier have access to a dedicated Slack channel with a guaranteed 1-hour SLA for critical issues.
- **Standard Support:** Submit a ticket via the "Support" widget in the bottom right corner of the dashboard. Our engineering team investigates all parsing and sandbox failures to continuously improve the platform.
