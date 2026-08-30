# Managing Repositories

At its core, API Guardian is a platform designed to protect and maintain source code. The **Repositories** management section is where you connect your organization's intellectual property to our autonomous intelligence engine. 

## Ingestion and Synchronization
When you connect a repository via the GitHub integration, API Guardian immediately begins the ingestion process. We securely clone the default branch (usually `main` or `master`) into an ephemeral, encrypted volume. 

Our high-performance parsers scan the codebase to identify the language runtime (Node.js, Python, Go, etc.) and construct a comprehensive Abstract Syntax Tree (AST) graph. This graph maps every function, class, and external API call. Once the initial parsing is complete, we establish a secure webhook with GitHub. Whenever a developer pushes a new commit to the default branch, we receive a delta payload and update our internal AST graph in real-time. This ensures our intelligence is always synchronized with your latest code.

## The Repository Dashboard
Navigating to a specific repository in the API Guardian dashboard provides a wealth of actionable intelligence:
- **Dependency Health Score:** An aggregate metric indicating how many of your external API dependencies are currently using deprecated or soon-to-be-sunset versions.
- **Active Cases:** A list of all ongoing autonomous maintenance operations specifically targeting this repository.
- **Guarded API Footprint:** A visual map showing exactly which files in this repository interact with which third-party APIs.

## Per-Repository Configuration
While you can set global defaults at the Organization level, you can override settings on a per-repository basis using the UI or a `guardian.yml` file. 

You can configure:
- **Test Commands:** Specify the exact command the Verification Sandbox should run (e.g., `npm run test:e2e`).
- **Ignore Paths:** Prevent the AST parser from scanning specific directories (like `node_modules`, `vendor`, or legacy submodules).
- **PR Routing:** Automatically assign Pull Requests generated for this repository to a specific engineering squad.

By providing granular control and deep visibility into every connected repository, API Guardian empowers your engineering teams to manage automated maintenance at any scale.
