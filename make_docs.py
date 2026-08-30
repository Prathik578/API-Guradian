import os

docs_dir = 'frontend/docs-content'
os.makedirs(docs_dir, exist_ok=True)

docs = {
    'introduction': '# Introduction\n\nWelcome to API Guardian. This platform automates the maintenance of third-party API dependencies.',
    'quickstart': '# Quickstart\n\n1. Sign up.\n2. Connect GitHub.\n3. Add a Guarded API.',
    'how-it-works': '# How it Works\n\nAPI Guardian uses deterministic AI to monitor, map, migrate, and verify API updates.',
    'core-concepts': '# Core Concepts\n\n- **Tenants**: Organizations using the platform.\n- **Guarded APIs**: External APIs being monitored.\n- **Repositories**: Codebases integrated via GitHub.',
    'guarded-apis': '# Guarded APIs\n\nMonitor your dependencies for breaking changes.',
    'repositories': '# Repositories\n\nConnect GitHub to sync your code.',
    'provider-changes': '# Provider Changes\n\nDetected updates from upstream API providers.',
    'provider-notices': '# Provider Notices\n\nAlerts indicating deprecations or sunsetting of APIs.',
    'impact-analysis': '# Impact Analysis\n\nAPI Guardian analyzes the exact files and lines affected by an API change.',
    'replacement-mapping': '# Replacement Mapping\n\nMaps deprecated API calls to their new equivalents.',
    'migration': '# Migration\n\nAutomatically applies code patches to your repository.',
    'verification': '# Verification\n\nRuns sandbox tests to cryptographically prove the migration is safe.',
    'evidence': '# Evidence\n\nLogs and artifacts proving the correctness of a patch.',
    'github-integration': '# GitHub Integration\n\nOAuth based integration to manage Pull Requests and Code access.',
    'pull-requests': '# Pull Requests\n\nAutomatically created PRs with deterministic patches.',
    'authentication': '# Authentication\n\nSecure login using bcrypt hashing and JWT tokens.',
    'organizations': '# Organizations\n\nMulti-tenant isolation for all resources.',
    'members': '# Members\n\nManage users within your organization.',
    'rbac': '# RBAC\n\nRole-Based Access Control: OWNER, ADMIN, MEMBER, VIEWER.',
    'mfa': '# MFA\n\nMulti-Factor Authentication using TOTP.',
    'activity-logs': '# Activity Logs\n\nAudit trails of all actions taken in the organization.',
    'notifications': '# Notifications\n\nAlerts for migrations, changes, and system events.',
    'usage-and-quotas': '# Usage and Quotas\n\nTrack your usage against your organization plan limits.',
    'integrations': '# Integrations\n\nManage connections to GitHub and other providers.',
    'security': '# Security\n\nStrict tenant isolation, IAM roles, and secure sandbox execution.',
    'architecture': '# Architecture\n\nFastAPI backend, Next.js frontend, PostgreSQL DB, Celery workers.',
    'api-reference': '# API Reference\n\nREST API for all platform functionality.',
    'configuration': '# Configuration\n\nSystem configuration using environment variables.',
    'environment-variables': '# Environment Variables\n\nKeys like `DATABASE_URL`, `GITHUB_CLIENT_ID`, etc.',
    'local-development': '# Local Development\n\nRun `docker-compose up` to start the local stack.',
    'deployment': '# Deployment\n\nDeploy using AWS Fargate, RDS, and ElastiCache.',
    'aws-runtime': '# AWS Runtime\n\nProduction environment on AWS.',
    'troubleshooting': '# Troubleshooting\n\nCommon issues and resolutions.',
    'known-limitations': '# Known Limitations\n\n**IMPLEMENTED**: Core workflow, GitHub OAuth, Tenant isolation, Quotas, Password Reset.\n**EXTERNAL INFRASTRUCTURE REQUIRED**: Real Sandbox execution requires AWS Fargate. Email delivery requires SMTP.\n**MOCKED**: Stripe sync is mocked for MVP.'
}

for slug, content in docs.items():
    with open(os.path.join(docs_dir, f'{slug}.md'), 'w') as f:
        f.write(content)
