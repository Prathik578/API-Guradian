# Security

Security is the foremost priority of API Guardian, reflecting its enterprise-grade design and operational model.

## Identity & Access Management
- **Authentication**: JWT-based session management backed by bcrypt-hashed passwords.
- **Multi-Factor Authentication (MFA)**: TOTP implementation required for sensitive actions.
- **Role-Based Access Control (RBAC)**: Enforces OWNER, ADMIN, MEMBER, and VIEWER roles across all endpoints.

## Multi-Tenancy & Data Isolation
- **Row-Level Security (RLS)**: Active on all tenant-scoped tables within the PostgreSQL database.
- **Session Context**: Enforced aggressively by `TenantContext` to prevent data leakage.

## Code Execution Isolation
- **Sandbox Security**: Execution of all customer patches occurs in unprivileged AWS Fargate containers with zero-trust network policies, meaning outbound data access and host resource mounting are aggressively blocked.
- **Cryptographic Evidence**: All tests produce signed verification payloads using deterministic hashing to prevent tampering.
