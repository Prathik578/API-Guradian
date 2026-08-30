# Environment Variables Reference

If you are running API Guardian locally for development, or if you are managing an Enterprise BYOC (Bring Your Own Cloud) deployment, understanding the environment variables is critical for proper operation. 

The platform uses a `.env` file (or standard OS environment variables) to configure everything from database connections to external API keys.

## Core Services
- `DATABASE_URL`: The primary connection string for the PostgreSQL database. Must include credentials and port. Example: `postgresql+psycopg2://user:password@localhost:5432/api_guardian`
- `REDIS_URL`: The connection string for the Redis instance used for caching, rate limiting, and Celery task brokering. Example: `redis://localhost:6379/0`
- `NEXT_PUBLIC_API_URL`: Used by the Next.js frontend to locate the backend REST API. Defaults to `http://127.0.0.1:8000`.

## Security & Authentication
- `SECRET_KEY`: A highly complex, securely generated cryptographic string used for signing JWT authentication tokens. **Never expose this.**
- `CORS_ORIGINS`: A comma-separated list of allowed origins for Cross-Origin Resource Sharing. Example: `http://localhost:3000,https://app.apiguardian.com`

## Third-Party Integrations
- `GITHUB_CLIENT_ID`: The OAuth Client ID provided by GitHub when registering the API Guardian GitHub App.
- `GITHUB_CLIENT_SECRET`: The corresponding OAuth Client Secret.
- `GITHUB_WEBHOOK_SECRET`: The cryptographic secret used to verify that incoming webhooks genuinely originated from GitHub.

## AWS Integration (For Verification Sandboxes)
- `AWS_ACCESS_KEY_ID`: Used by the execution engine to spin up Fargate tasks.
- `AWS_SECRET_ACCESS_KEY`: The corresponding secret key.
- `AWS_REGION`: The region where the sandboxes should be executed (e.g., `us-east-1`).
- `S3_ARTIFACT_BUCKET`: The name of the S3 bucket used for storing cloned repositories, generated patches, and verification logs.

Ensure that all environment variables are securely injected using a secret manager (like AWS Secrets Manager or HashiCorp Vault) in production environments.
