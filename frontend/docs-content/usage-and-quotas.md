# Usage, Quotas, and Billing

API Guardian operates on a transparent, usage-based billing model designed to scale seamlessly with your engineering organization, whether you are a small startup or a Fortune 500 enterprise. This document outlines how usage is calculated and how quotas are enforced.

## Understanding Usage Metrics
Billing and quotas in API Guardian are entirely based on value delivered, not artificial constraints like per-seat licenses. We track three primary metrics:

1. **Active Repositories:** The number of GitHub repositories you have connected and authorized API Guardian to actively monitor and parse.
2. **Guarded APIs:** The number of distinct third-party API providers you have configured the intelligence engine to monitor for notices.
3. **Verification Compute Minutes:** The total amount of time (in minutes) that the AWS Fargate Verification Sandboxes spend executing your test suites to validate generated patches.

## Quotas and Limits
To protect the platform from abuse and runaway execution loops, strict quotas are enforced at the Organization level:
- **Sandbox Timeouts:** By default, a single Verification Sandbox execution is hard-capped at 15 minutes. If your test suite takes longer, the execution will be terminated, and the case will fail. (This limit can be raised for Enterprise tiers).
- **Rate Limits:** Automated API interactions using Personal Access Tokens are limited to 1,000 requests per minute to ensure Control Plane stability.

## Monitoring Your Usage
Complete transparency is available in the **Usage & Billing** tab within the Administration dashboard. 
Here you can view:
- Real-time charts detailing your compute minutes consumed this billing cycle.
- A breakdown of which repositories are consuming the most verification resources.
- Forecasting models predicting your end-of-month invoice based on current trajectory.

You can configure Billing Alerts to receive an email or Slack notification if your organization exceeds a specific spending threshold, ensuring you are never surprised by an invoice. By aligning our billing perfectly with the maintenance toil we eliminate, API Guardian guarantees a massive Return on Investment (ROI) for every compute minute consumed.
