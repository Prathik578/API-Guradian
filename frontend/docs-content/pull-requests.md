# Pull Requests: The Final Deliverable

The ultimate goal of the entire API Guardian pipeline—from detection and AST parsing to LLM generation and Fargate verification—is to produce a single, actionable artifact: the **Pull Request** (PR). 

We firmly believe that autonomous AI agents should not blindly push code into production. The Pull Request is the perfect interface for human-AI collaboration. It allows the autonomous system to do the heavy lifting while reserving the final approval for a human engineer.

## The Anatomy of an API Guardian PR
When API Guardian opens a Pull Request on your GitHub repository, it is not a sparse, confusing diff. It is a highly detailed, beautifully formatted document designed to provide maximum context to the human reviewer. 

Every PR includes:
1. **The Executive Summary:** A clear explanation of *why* this PR exists, directly linking to the upstream Provider Notice that triggered the workflow.
2. **The Migration Plan:** The detailed strategy that the LLM followed to safely refactor the code.
3. **The Blast Radius:** A list of the specific files and functions that were modified.
4. **The Cryptographic Evidence:** The digital signature and test logs proving that the patch passed all unit and integration tests inside the isolated Verification Sandbox.

## Configuration and Workflows
API Guardian PRs fit seamlessly into your existing GitOps workflows. Depending on your repository configuration (`guardian.yml`), you can dictate exactly how these PRs are handled:
- **Draft Mode:** PRs can be opened as "Drafts" by default, allowing engineers to review the code before triggering expensive internal CI/CD pipelines.
- **Auto-Assignment:** The system can automatically request reviews from specific GitHub Teams (e.g., `@organization/security-reviewers`) or assign the PR to the engineer who last modified the affected files.
- **Labeling:** PRs are automatically tagged with custom labels (e.g., `api-guardian`, `automated-maintenance`, `high-priority`) to help you filter and route them appropriately.

## Human-in-the-Loop Refinement
If an engineer reviews the PR and requests changes, API Guardian listens. You can simply leave a comment on the PR (e.g., *"Please extract this logic into a helper function"*). The platform detects the comment, routes it back to the LLM context window, generates an updated patch, re-runs the Verification Sandbox, and pushes a new commit to the branch. 

This iterative, conversational interface transforms API Guardian from a static tool into a truly collaborative, junior engineering partner.
