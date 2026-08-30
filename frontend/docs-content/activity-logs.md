# Activity Logs: The Immutable Record

In enterprise software development, visibility is paramount. The Activity Logs in API Guardian provide a comprehensive, immutable, and detailed record of every single action that occurs within your organization. 

## The Anatomy of a Log Entry
Every time a user logs in, a setting is changed, a Pull Request is generated, or a Provider Notice is ingested, an activity log is created. These logs are not just simple strings; they are structured data objects containing:
- **Timestamp:** Precise to the millisecond.
- **Actor:** Who performed the action? Was it a user (identified by email) or a system component (like the AST parser or the Fargate sandbox)?
- **Action Type:** A categorized, filterable enum representing the operation.
- **Context:** The resource that was affected (e.g., the specific GitHub Repository ID or the Provider Notice ID).
- **IP Address & User Agent:** For security and auditing purposes.

## Security and Compliance
For organizations operating in regulated industries (finance, healthcare, government), audit logs are not optional; they are legally required. API Guardian's Activity Logs are designed to meet SOC2, HIPAA, and GDPR compliance standards. 

The logs are append-only. Once an event is written, it cannot be modified or deleted, even by organization owners. This ensures complete forensic integrity in the event of a security review or compliance audit.

## Filtering and Exporting
Navigating thousands of events is effortless with our advanced filtering system. You can drill down by date ranges, specific actors, or event severity levels. 

Need to analyze the data in your own SIEM (Security Information and Event Management) system? API Guardian allows you to export your logs via CSV or forward them in real-time using secure webhooks to platforms like Splunk, Datadog, or ElasticSearch.
