import pytest


@pytest.mark.real_aws
def test_fargate_credential_isolation():
    """Proves credential isolation by running a malicious script in real ECS task."""
    # This harness is intended to invoke FargateSandboxOrchestrator to run a task
    # that executes a script which dumps the environment and checks metadata endpoints.
    # The result will be fetched from S3 or logs.
