# Configuration

API Guardian is heavily configurable via environment variables.

## Required Variables
- `DATABASE_URL`: The PostgreSQL connection string. (Required)
- `REDIS_URL`: The Redis connection string for Celery. (Required)
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`: GitHub OAuth credentials. (Required for Git Integration)
- `OPENAI_API_KEY`: Key for the LLM Gateway. (Required for Migration generation)
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`: Required for Sandbox execution.
- `JWT_SECRET`: Secret used for signing authentication tokens.

*Note: For local development, missing external provider keys will cause those specific features to return 501 Not Implemented.*
