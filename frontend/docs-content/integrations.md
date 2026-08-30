# Integrations Ecosystem

API Guardian is not a silo. To be truly effective, an autonomous maintenance platform must plug seamlessly into your existing workflows, communication channels, and observability stacks. The **Integrations Ecosystem** allows you to connect API Guardian to the tools your team already uses every day.

## Communication & Alerting
- **Slack:** Connect API Guardian to your Slack workspace. Receive real-time notifications in specific channels when a high-severity Provider Notice is detected, when a new Maintenance Case is opened, or when a Pull Request is ready for review. The Slack integration supports interactive buttons, allowing you to approve or dismiss cases directly from your chat client.
- **Microsoft Teams:** Similar to Slack, receive adaptive cards in Teams channels summarizing API changes and blast radius impact.
- **PagerDuty / OpsGenie:** For critical dependencies, you can route immediate sunset warnings or sudden breaking changes directly to your on-call engineers via PagerDuty or OpsGenie incidents.

## CI/CD and DevOps
- **GitHub Actions / GitLab CI:** While API Guardian runs its own verification sandboxes, you can configure the system to trigger your existing CI/CD pipelines via webhooks as a secondary validation step.
- **SonarQube:** Automatically push the generated code patches through SonarQube static analysis before the PR is opened to ensure compliance with internal code quality metrics.

## Observability and SIEM
- **Datadog / New Relic:** Forward internal API Guardian metrics (such as the number of APIs guarded, active maintenance cases, and successful migrations) to your existing dashboards.
- **Splunk / Elastic (ELK):** Export the immutable Activity Logs via secure, real-time webhooks for long-term retention and security analysis in your enterprise SIEM.

By weaving API Guardian into your existing operational fabric, you ensure that autonomous API maintenance enhances your workflows without requiring your team to learn a completely new set of operational habits.
