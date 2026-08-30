# Notifications: Intelligent Alerting

In an autonomous system, effective communication is the difference between seamless operation and silent failure. API Guardian is designed to be an invisible background process, but when it needs your attention, it must deliver the right information, to the right person, at the right time. 

The **Notifications** engine governs all outbound communication from the platform.

## In-App Notifications
The primary interface for non-critical alerts is the in-app notification center, accessible via the bell icon in the dashboard's top navigation bar. 

Here, you will receive real-time updates via WebSockets regarding the lifecycle of your automated maintenance:
- **Case Opened:** When the system detects a relevant Provider Notice and begins AST parsing.
- **Verification Started:** When a generated patch is deployed to the Fargate sandbox for testing.
- **Verification Passed:** When the cryptographic evidence payload is successfully signed.
- **PR Ready:** When a Pull Request has been opened on your repository and is awaiting human review.

## Email Digests
Not everyone wants to monitor a dashboard constantly. API Guardian provides highly configurable email digests. You can choose to receive immediate emails for critical events (like a Verification Sandbox failure), or you can opt for a weekly digest summarizing all autonomous maintenance performed across your organization over the past 7 days.

## Webhook Routing
For enterprise teams, the true power of the Notification engine lies in Webhook Routing. You can configure granular rules to forward specific events to external systems. 
- Route `HIGH_SEVERITY_NOTICE` events directly to a PagerDuty service.
- Route `PR_READY_FOR_REVIEW` events to a specific Slack channel, tagging the code owners of the affected repository.
- Route `MIGRATION_FAILED` events to a Jira webhook to automatically create a tracking ticket for manual intervention.

## Notification Policies and Noise Reduction
Alert fatigue is a serious problem in modern DevOps. API Guardian combats this by allowing Organization Admins to configure global Notification Policies. You can suppress alerts for Low Severity notices, bundle multiple alerts into a single digest, and ensure that only the engineers actually responsible for a specific repository receive alerts related to it. 

By delivering intelligent, context-aware notifications, API Guardian ensures you are always informed but never overwhelmed.
