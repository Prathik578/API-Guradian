# Security Architecture: Built for Enterprise Trust

When you grant an external platform access to your source code and API credentials, security is not just a feature—it is the foundational pillar of the entire product. API Guardian was engineered from day one to exceed the most stringent enterprise security requirements, employing defense-in-depth strategies, strict tenant isolation, and zero-trust architectures.

## Strict Tenant Isolation (RLS)
Data bleeding between customers is the cardinal sin of SaaS. To prevent this, API Guardian utilizes PostgreSQL Row-Level Security (RLS) at the database layer. 

Every single database query is cryptographically scoped to the current user's `tenant_id`. Even if a bug were introduced in the application logic, the database engine itself would reject any query attempting to read or write data belonging to another organization. Your data is mathematically isolated.

## The AWS Fargate Sandbox
Our verification pipeline executes untrusted code (both your application code and the AI-generated patches). To ensure this code cannot compromise our infrastructure or access sensitive data, we execute all verification jobs in ephemeral AWS Fargate tasks. 

These sandboxes are:
- **Ephemeral:** They exist only for the duration of a single test run and are permanently destroyed immediately after.
- **Isolated:** They run in dedicated VPC subnets with strict Security Groups.
- **Network-Restricted:** They have no route to the public internet, completely eliminating data exfiltration risks.
- **Resource-Constrained:** They are strictly limited in CPU, memory, and execution time to prevent denial-of-service attacks.

## Secret Management
We never store your API keys or GitHub tokens in plaintext. All secrets are encrypted at rest using AWS Key Management Service (KMS) with customer-specific, rotating encryption keys. They are only decrypted in memory at the exact moment they are needed by the execution engine, and are immediately scrubbed from memory afterwards.

## Role-Based Access Control (RBAC)
Within your organization, you need fine-grained control over who can do what. API Guardian features a comprehensive RBAC system:
- **Owners:** Full control over billing, integrations, and organization settings.
- **Admins:** Can manage Guarded APIs, review Pull Requests, and configure notifications.
- **Members:** Can view dashboards, notices, and activity logs.

## Audit Logging and Compliance
Every single action taken within the platform—whether it's a user logging in, an AI agent generating a patch, or a webhook being triggered—is meticulously logged in our immutable Activity Log. This provides a complete forensic audit trail, ensuring that you always have total visibility into what is happening with your codebase. 

API Guardian is built to be the most secure piece of your infrastructure, guarding your APIs while guarding your data with uncompromising vigilance.
