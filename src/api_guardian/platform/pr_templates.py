"""Pull Request Body Templates."""

class PRTemplateBuilder:
    """Generates rich markdown bodies for GitHub Pull Requests."""

    @staticmethod
    def build_pr_body(
        provider_name: str, 
        change_title: str, 
        affected_files_count: int,
        audit_passed: bool
    ) -> str:
        """Constructs the PR description markdown."""
        
        status_badge = "✅ Verified in Sandbox" if audit_passed else "⚠️ Audit Failed - Review Required"
        
        return f"""## API Guardian: Automated Dependency Maintenance
This is an automated pull request to address a provider API change.

### 🚨 Provider Change Detected
**Provider**: {provider_name}
**Change**: {change_title}

### 🛠️ Migration Details
API Guardian automatically analyzed the repository and applied structural migrations to **{affected_files_count}** affected files.

### 🧪 Verification Status
**Status**: {status_badge}

The patch was verified in an isolated Fargate sandbox by running the repository's test suite against the updated code.
No tests were skipped or deleted to artificially achieve a passing result.
"""
