# Managing Organization Members

Software engineering is a team sport, and API Guardian is built to support organizations of all sizes, from small startups to massive global enterprises. The **Members** management section allows you to invite your colleagues, assign roles, and maintain a secure access control perimeter around your automated maintenance operations.

## Inviting New Members
To invite a colleague, navigate to the **Members** tab in the dashboard Administration section. Click "Invite Member" and enter their email address. 

The system will dispatch a secure, time-limited cryptographic invitation link to their inbox. Upon clicking the link, they will be prompted to create an account and will automatically be added to your Organization Workspace.

## Role-Based Access Control (RBAC)
When inviting a member, or at any time thereafter, you must assign them a Role. API Guardian utilizes a strict RBAC model to ensure least privilege:

- **OWNER:** The highest level of access. Owners can manage billing, delete the organization, change the underlying GitHub integrations, and promote other users to Owner status.
- **ADMIN:** Admins have full operational control over the maintenance lifecycle. They can add or remove Guarded APIs, configure webhook notifications, manually trigger migrations, and override configuration settings.
- **MEMBER:** The standard role for software engineers. Members can view the dashboard, read Provider Notices, inspect generated Pull Requests, and read the Verification Sandbox logs. They cannot alter platform configurations.
- **VIEWER:** A read-only role perfect for compliance officers or external auditors. Viewers can read the Activity Logs and dashboards but cannot interact with the maintenance cases.

## Revoking Access
When an employee leaves the company, you can instantly revoke their access from the Members dashboard. Thanks to our centralized JWT authentication mechanism, revoking a member instantly terminates all their active sessions and API tokens, ensuring your intellectual property and platform configurations remain perfectly secure.
