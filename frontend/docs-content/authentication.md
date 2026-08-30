# Authentication Strategy

Authentication in API Guardian is designed to balance frictionless user experience with uncompromising enterprise security. We employ a modern, token-based authentication architecture that seamlessly handles both interactive user sessions and automated API access.

## JWT (JSON Web Tokens)
All authentication within the platform utilizes JSON Web Tokens (JWT). When a user successfully authenticates, they are issued a cryptographically signed JWT. This token contains standard claims such as the subject (`sub`), expiration time (`exp`), and issued-at time (`iat`). 

Crucially, the token does *not* contain sensitive database IDs or permissions in plaintext. Instead, it serves as a secure reference that the Control Plane validates against the database on every request.

## Session Management
For users accessing the dashboard via a web browser, the JWT is securely stored in an HTTP-Only, Secure, SameSite=Lax cookie. This approach fundamentally mitigates the risk of Cross-Site Scripting (XSS) attacks stealing the token, as JavaScript cannot access HTTP-Only cookies.

## API Access Tokens
For programmatic access (e.g., CI/CD integrations or custom scripts), users can generate Personal Access Tokens (PATs). These tokens are long-lived and can be revoked at any time from the dashboard. For absolute security, PATs are only shown to the user once upon creation. We store only a one-way cryptographic hash of the token in our database, meaning that even if our database were compromised, the plaintext tokens could never be recovered.

## Multi-Factor Authentication (MFA)
API Guardian strongly recommends (and for Enterprise tiers, enforces) Multi-Factor Authentication. We support Time-based One-Time Passwords (TOTP) compatible with apps like Google Authenticator, Authy, and 1Password. When MFA is enabled, the initial login step returns an intermediate token that must be immediately exchanged along with the 6-digit TOTP code to complete the authentication flow.
