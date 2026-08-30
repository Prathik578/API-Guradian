# Organization Workspaces

API Guardian is designed around a multi-tenant architecture. The fundamental boundary for data isolation, billing, and configuration is the **Organization**. Whether you are an individual developer, an open-source maintainer, or a multinational corporation, your work within API Guardian occurs within the context of an Organization Workspace.

## The Tenant Boundary
Every piece of data in the platform—from connected GitHub repositories and Guarded APIs, to Activity Logs and Verification Sandbox configurations—is cryptographically bound to a specific Organization ID (`tenant_id`). 

We utilize PostgreSQL Row-Level Security (RLS) to ensure that it is mathematically impossible for data to bleed across organization boundaries. When you are operating within your Organization, you have absolute assurance that your source code, infrastructure metrics, and configuration details are completely isolated from all other tenants on the platform.

## Managing Multiple Organizations
Many engineers work across multiple contexts—for example, contributing to an open-source project while also working for a commercial employer. API Guardian seamlessly supports this. 

A single User Account (identified by your email address) can be a member of multiple Organizations simultaneously. You can seamlessly switch between these active workspaces using the Organization Switcher in the top navigation bar. Each workspace maintains its own distinct RBAC permissions, integrations, and billing settings.

## Organization Settings
As an Organization Owner, you have access to the global settings panel. Here you can define:
- **Organization Profile:** Set the display name and logo for your workspace.
- **Default Policies:** Configure global rules, such as requiring Draft PRs by default or mandating specific reviewer groups for all autonomous Pull Requests.
- **Data Retention:** Configure how long Activity Logs and Verification payloads should be stored to comply with your internal corporate data governance policies.

The Organization is the bedrock of your experience in API Guardian, providing a secure, isolated, and highly configurable environment for autonomous maintenance.
