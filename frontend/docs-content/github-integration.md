# GitHub Integration Guide

API Guardian's seamless integration with GitHub is what allows us to monitor your codebase, analyze the blast radius of upstream API changes, and autonomously open Pull Requests. We operate as a deeply integrated GitHub App, utilizing modern, secure Webhook and API architectures.

## Installing the GitHub App
To begin, navigate to the **Integrations** tab in your dashboard and click "Connect GitHub". You will be redirected to GitHub's authorization page. 

You have granular control over installation:
- **All Repositories:** API Guardian will automatically monitor all current and future repositories in your organization. This is recommended for maximum protection.
- **Selected Repositories:** You can manually select specific repositories to grant access to. 

## Required Permissions
API Guardian follows the principle of least privilege. The GitHub App requests only the permissions necessary to function:
- **Repository Contents (Read/Write):** Read access is required to clone the code for AST parsing. Write access is strictly limited to creating new branches and committing the generated migration patches.
- **Pull Requests (Read/Write):** Required to open the final PR, update descriptions with migration plans, and read review comments for human-in-the-loop interactions.
- **Webhooks (Read):** We listen for push events to keep our internal AST graphs synchronized with your latest `main` branch.

## How We Interact with Your Repo
API Guardian is designed to be a polite and unobtrusive collaborator. 
1. **Branching Strategy:** When a patch is ready, we create a new branch from your default branch (usually `main`), formatted as `api-guardian/update-[provider]-[version]`. We never commit directly to protected branches.
2. **Draft PRs:** If configured in your settings, API Guardian can open Pull Requests in "Draft" mode, allowing your team to review the changes without triggering CI/CD pipelines unnecessarily.
3. **Impeccable Commits:** The generated commits are highly descriptive, conventionally formatted, and cryptographically signed by the API Guardian bot, ensuring a clean and professional git history.

By integrating deeply with GitHub, API Guardian becomes an invisible, autonomous member of your engineering team.
