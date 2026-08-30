# Role-Based Access Control (RBAC)

Security in a collaborative enterprise platform requires granular control over who can perform specific actions. API Guardian implements a comprehensive Role-Based Access Control (RBAC) architecture that adheres to the principle of least privilege, ensuring that users only have the permissions necessary to perform their job functions.

## The Permission Matrix
Permissions in API Guardian are not granted ad-hoc; they are bundled into predefined Roles. Every member of an Organization is assigned exactly one Role. 

### 1. OWNER
The Owner role possesses absolute authority over the Organization Workspace.
- **Capabilities:** Can delete the organization, manage billing and credit cards, configure SAML/SSO integration, revoke GitHub App authorizations, and promote other users to Owner status.
- **Use Case:** CTOs, VP of Engineering, or dedicated DevOps leads.

### 2. ADMIN
Admins manage the operational maintenance lifecycle but lack destructive organizational capabilities.
- **Capabilities:** Can invite or remove Members and Viewers. Can add or remove Guarded APIs. Can configure webhook destinations and change global repository settings. Can manually trigger or cancel Migration Cases.
- **Use Case:** Engineering Managers, Tech Leads, or senior developers responsible for specific microservices.

### 3. MEMBER
The standard role for software engineers interacting with the platform daily.
- **Capabilities:** Read-only access to organizational settings. Can view dashboards, browse Provider Notices, inspect AST impact graphs, and read Verification Sandbox execution logs. Cannot alter the configuration of Guarded APIs or disconnect integrations.
- **Use Case:** Software Engineers, QA Automation Engineers.

### 4. VIEWER
A strictly read-only role designed for transparency without risk.
- **Capabilities:** Can view the Activity Logs, compliance reports, and high-level analytics dashboards. Cannot view source code diffs or interact with Maintenance Cases.
- **Use Case:** Compliance Officers, IT Auditors, or external security consultants.

## Implementation Details
Our RBAC system is enforced at the API layer using strict FastAPI dependency injection. Every single endpoint checks the user's role extracted from the database against a required permission list before executing any logic. If a user attempts to access an endpoint they lack permission for, the API immediately returns a `403 Forbidden` status code, and the unauthorized attempt is permanently recorded in the Activity Log for auditing.
