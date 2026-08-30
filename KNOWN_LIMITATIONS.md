# Known Limitations

API Guardian is currently in an MVP state and has the following known boundaries:

## IMPLEMENTED
- Core Backend Architecture, ORM, and Migration tooling.
- Row Level Security (RLS) and Tenant isolation.
- Authentication (Bcrypt + JWT + MFA support) and Multi-Tenant RBAC.
- Password Reset Flow (End-to-end token generation & verification).
- Usage and Quota Tracking UI/API.
- Complete GitHub OAuth flow with Secure Credential Storage and Repository Syncing.

## MOCKED / STUBBED
- Stripe integration synchronization is currently mocked for demonstrations.
- Webhook signature validation for specific third-party providers.

## EXTERNAL INFRASTRUCTURE REQUIRED
- **AWS Sandbox**: Deterministic verification requires actual AWS Fargate configuration to execute securely. Without AWS keys, sandbox verification is simulated or skipped.
- **Email Delivery**: The password reset token generation is implemented securely, but the email dispatch system requires an external SMTP provider which is unconfigured. The system cleanly returns `501 Not Implemented` for email delivery.
